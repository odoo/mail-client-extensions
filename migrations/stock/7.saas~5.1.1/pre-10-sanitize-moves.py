import logging

from openerp.addons.base.maintenance.migrations import util

NS = 'openerp.addons.base.maintenance.migrations.stock.saas-5.'
_logger = logging.getLogger(NS + __name__)

MINIMUM_ROUNDING = 1e-06

def sanitize_moves(cr):
    fixed_moves = 0
    product_product_uom_unit = util.ref(cr, 'product.product_uom_unit')

    # 1. Fix stock moves with a precision greater than 15 because they probably
    #    come from a bad calculation and also because this can't be handled
    #    properly anyway
    cr.execute("""
        UPDATE  stock_move
        SET     product_uos_qty = product_uos_qty::double precision
        ,       product_qty = product_qty::double precision
        WHERE   mod(product_uos_qty, 1e-15) != 0
        OR      mod(product_qty, 1e-15) != 0
        RETURNING id
        """)
    if cr.rowcount:
        fixed_moves += cr.rowcount
        _logger.warn("[Quantities of %s stock moves adjusted] precision "
                     "required greater than 15 decimals",
                     cr.rowcount)

    # 2. Automatically fix UoM with rounding = 0
    cr.execute("""
        SELECT
            uom.id AS id,
            coalesce(pow(10, -max(
                char_length(split_part(trim(both '0'
                                            from product_qty::varchar),
                                       '.', 2)))), 1) AS new_rounding
        FROM        product_uom uom
        LEFT JOIN   stock_move move
            ON      move.product_uom = uom.id
        WHERE       uom.rounding = 0
        GROUP BY    uom.id
        """)
    for uom_id, new_rounding in cr.fetchall():
        _logger.warn("[UoM %s rounding adjusted to %s] rounding was 0",
                     uom_id, new_rounding)
        assert new_rounding >= MINIMUM_ROUNDING, \
            "UoM's rounding adjustment too small, manual check required"
        cr.execute("UPDATE product_uom SET rounding = %s WHERE id = %s",
                   [new_rounding, uom_id])

    # 3.1 check that stock move's quantity can be converted to product template
    #     quantity without losing precision
    cr.execute("""
        SELECT  array_agg(move.id) AS moves
        ,       temp_uom.id AS uom
        ,       pow(10, -max(char_length(
                    split_part(trim(both '0' from
                                    (move.product_qty / move_uom.factor
                                           * temp_uom.factor)
                                    ::double precision::varchar),
                               '.', 2)))) AS new_rounding
        FROM    stock_move move
        JOIN    product_uom move_uom ON move_uom.id = move.product_uom
        JOIN    product_product prod ON prod.id = move.product_id
        JOIN    product_template temp ON temp.id = prod.product_tmpl_id
        JOIN    product_uom temp_uom ON temp_uom.id = temp.uom_id
        -- NOTE: it's important to check also the moves that have the same UoM
        --       than the product template because it is possible that the next
        --       step will create a new UoM based on original UoM and they will
        --       have the same factor. If the original UoM lacks of precision,
        --       it will be a problem.
        -- NOTE: it's *also* important to check the moves that have different
        --       UoM's category than the product template because the category
        --       will be fixed in the second section/fix anyway and they still
        --       need to be convertible to the product's UoM.
        WHERE   mod((move.product_qty / move_uom.factor * temp_uom.factor)
                    ::double precision::numeric, temp_uom.rounding) != 0
        GROUP BY temp_uom.id
        """)
    for moves, uom, new_rounding in cr.fetchall():
        _logger.warn("[UoM %s rounding adjusted to %s] not enough precision "
                     "to store quantity of %s stock moves: %s",
                     uom, new_rounding, len(moves),
                     ", ".join(map(str, sorted(moves))))
        assert new_rounding >= MINIMUM_ROUNDING, \
            "UoM's rounding adjustment too small, manual check required"
        cr.execute("UPDATE product_uom SET rounding = %s WHERE id = %s",
                   [new_rounding, uom])
        if not uom == product_product_uom_unit:
            fixed_moves += len(moves)

    # 3.2 check for multiple inconsistencies in stock moves, cfr comments
    #     in the query
    cr.execute("""
        SELECT  array_agg(move.id) AS moves
        ,       least(pow(10, -max(char_length(
                          split_part(trim(both '0' from move.product_qty::varchar),
                               '.', 2)))),
                      move_uom.rounding) AS new_rounding
        ,       move_uom.id AS move_uom
        ,       temp_uom.category_id AS temp_uom_cat
        FROM    stock_move move
        JOIN    product_uom move_uom ON move_uom.id = move.product_uom
        JOIN    product_product prod ON prod.id = move.product_id
        JOIN    product_template temp ON temp.id = prod.product_tmpl_id
        JOIN    product_uom temp_uom ON temp_uom.id = temp.uom_id
        -- check that a move doesn't use a UoM that lacks of precision to
        -- store the quantity
        WHERE   mod(move.product_qty, move_uom.rounding) != 0
        -- check move's UoM category
        OR      move_uom.category_id != temp_uom.category_id
        GROUP BY move_uom.id, temp_uom.category_id
        """)
    for moves, new_rounding, move_uom, temp_uom_cat in cr.fetchall():
        _logger.warn("[UoM created based on UoM %s "
                     "(rounding=%s, category=%s)] "
                     "bad UoM's category or rounding for %s stock moves: %s",
                     move_uom, new_rounding, temp_uom_cat,
                     len(moves), ", ".join(map(str, sorted(moves))))
        assert new_rounding >= MINIMUM_ROUNDING, \
            "UoM's rounding adjustment too small, manual check required"
        cr.execute("""
            SELECT * INTO TEMP temp_uom FROM product_uom WHERE id = %s;
            UPDATE  temp_uom
            SET     category_id = %s
            ,       rounding = %s
            ,       active = false
            ,       id = nextval('product_uom_id_seq'::regclass);
            WITH new_uom AS (
                INSERT INTO product_uom (SELECT * FROM temp_uom) RETURNING *
            )
            UPDATE  stock_move
            SET     product_uom = (SELECT id FROM new_uom)
            WHERE   id = ANY(%s);
            DROP TABLE temp_uom;
            """, [move_uom, temp_uom_cat, new_rounding, moves])
        fixed_moves += len(moves)

    return fixed_moves

def check_moves(cr):
    # 1. Check if reconverting the rounding to the default UoM and back to the
    #    original UoM will give errors on stock moves
    cr.execute("""
        select
          m.id as move_id,
          m.product_qty as product_qty,
          m.product_uom as move_uom,
          um.category_id as move_uom_category,
          t.uom_id as default_uom,
          ut.category_id as default_uom_category,
          ut.factor as ut_factor,
          um.factor as um_factor,
          ut.rounding as ut_rounding,
          um.rounding as um_rounding,
          um.factor/ut.factor*(
           round(m.product_qty*ut.factor/um.factor,
                 ceil(-log(ut.rounding))::integer )) as computed_qty,
          round(
           um.factor/ut.factor*(round(
               m.product_qty*ut.factor/um.factor,
               ceil(-log(ut.rounding))::integer )),
           ceil(-log(um.rounding))::integer) as rounded_computed_qty
        from
          stock_move m
            inner join product_product p
              on p.id=m.product_id
            inner join product_template t
              on t.id=p.product_tmpl_id
            inner join product_uom um
              on um.id=m.product_uom
            inner join product_uom ut
              on ut.id=t.uom_id
        where
          t.uom_id != m.product_uom
            and
          m.product_qty != round(
            um.factor/ut.factor*(round(
                m.product_qty*ut.factor/um.factor,
                ceil(-log(ut.rounding))::integer )),
            ceil(-log(um.rounding))::integer)
        order by m.product_id, m.id;
        """)
    res = cr.dictfetchall()
    if res:
        for re in res:
            _logger.error(
                "Move {move_id}: qty: {product_qty} != {computed_qty} "
                "default UoM: {default_uom}, move UoM: {move_uom}, "
                "roundings: {ut_rounding}/{um_rounding}, "
                "factors: {ut_factor}/{um_factor}".format(**re))
        raise util.MigrationError("That was a bad move.")

    # 2. Check if the precision of the UoM of the stock moves is enough
    #    (assert the previous fix)
    cr.execute("""
        SELECT  array_agg(sm.id) AS move_ids
        ,       um.id AS uom
        ,       um.name AS name
        ,       um.rounding AS rounding
        FROM    stock_move sm, product_uom um
        WHERE   um.id = sm.product_uom
        AND     state NOT IN ('draft', 'cancel')
        AND     NOT mod(product_qty, um.rounding) = 0
        GROUP BY um.id
        """)
    assert cr.rowcount == 0, repr(cr.dictfetchall())

def migrate(cr, version):
    """
    performs various checks and try to fix the errors automatically
    """
    # count moves
    cr.execute("SELECT count(*) FROM stock_move")
    moves_count, = cr.fetchone()
    if not moves_count:
        return

    # fix moves
    fixed_moves = sanitize_moves(cr)
    check_moves(cr)
    assert sanitize_moves(cr) == 0, \
        "The code of fix_moves() is probably broken."

    # allow 1.5% of error, maybe we should increase
    # if less than 50 moves in the database, accept all changes...
    if moves_count > 50 and (float(fixed_moves) / float(moves_count)) > 0.015:
        raise util.MigrationError(
            "There is probably something wrong with the stock moves of the "
            "databases. Bad stock moves: %d/%d (%.01f%%)"
            % (fixed_moves, moves_count,
               (float(fixed_moves) / float(moves_count) * 100.0)))
