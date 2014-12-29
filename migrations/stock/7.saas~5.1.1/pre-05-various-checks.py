# -*- coding: utf-8 -*-
# performs various checks and try to fix the errors automatically

import logging

from openerp.addons.base.maintenance.migrations import util

_logger = logging.getLogger('openerp.addons.base.maintenance.migrations.stock.saas-5.checks')


def fix_moves(cr):
    fixed_moves = 0

    # 1. check if a given location is not linked to 2 or more wharehouses
    sql_check_location = """
        select wh.{field} as loc_id, loc.name, count(*), array_agg(wh.id) as wh_ids
        from stock_warehouse wh
            inner join stock_location loc
                on wh.{field}=loc.id
        group by wh.{field}, loc.name
        having count(*)  > 1"""

    loc_uniq_msgs = []
    for field in ['lot_input_id', 'lot_stock_id']:
        cr.execute(sql_check_location.format(field=field))
        checks = cr.dictfetchall()
        for check in checks:
            loc_uniq_msgs.append(
                ("Stock location '{name}' (id={loc_id}) is linked to more than " \
                "one warehouse (ids={wh_ids}). This is not allowed in Odoo version 8.0.\n" \
                "table: 'stock_warehouse', field: '{field}'").format(field=field, **check))

    if loc_uniq_msgs:
        msg = '\n'.join(loc_uniq_msgs)
        _logger.error(msg)
        raise util.MigrationError(msg)

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
        cr.execute("UPDATE product_uom SET rounding = %s WHERE id = %s",
                   [new_rounding, uom_id])

    # 3.2 check that stock move's quantity can be converted to product template
    #     quantity without losing precision
    cr.execute("""
        SELECT  array_agg(move.id) AS moves
        ,       temp_uom.id AS uom
        ,       pow(10, -max(char_length(
                    split_part(trim(both '0' from
                               (move.product_qty / move_uom.factor
                                * temp_uom.factor)::varchar),
                               '.', 2)))) AS new_rounding
        FROM    stock_move move
        JOIN    product_uom move_uom ON move_uom.id = move.product_uom
        JOIN    product_product prod ON prod.id = move.product_id
        JOIN    product_template temp ON temp.id = prod.product_tmpl_id
        JOIN    product_uom temp_uom ON temp_uom.id = temp.uom_id
        WHERE   mod((move.product_qty / move_uom.factor * temp_uom.factor),
                    temp_uom.rounding) != 0
        GROUP BY temp_uom.id
        """)
    for moves, uom, rounding in cr.fetchall():
        _logger.warn("[UoM %s rounding adjusted to %s] not enough precision "
                     "to store quantity of %s stock moves: %s",
                     uom, rounding, len(moves), ", ".join(map(str, moves)))
        cr.execute("UPDATE product_uom SET rounding = %s WHERE id = %s",
                   [rounding, uom])
        fixed_moves += len(moves)

    # 3.1 check for multiple inconsistencies in stock moves, cfr comments
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
    for moves, rounding, move_uom, temp_uom_cat in cr.fetchall():
        _logger.warn("[UoM created based on UoM %s "
                     "(rounding=%s, factor=%s, category=%s)] "
                     "bad UoM's category or rounding for %s stock moves: %s",
                     move_uom, rounding, rounding, temp_uom_cat,
                     len(moves), ", ".join(map(str, moves)))
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
            """, [move_uom, temp_uom_cat, rounding, moves])
        fixed_moves += len(moves)

    # assert the previous fix

    # 3.3 Check if reconverting the rounding to the default UoM and back to the
    #     original UoM will give errors on stock moves
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
            _logger.warn(
                "Move {move_id}: qty: {product_qty} != {computed_qty} "
                "default UoM: {default_uom}, move UoM: {move_uom}, "
                "roundings: {ut_rounding}/{um_rounding}, "
                "factors: {ut_factor}/{um_factor}".format(**re))
        raise util.MigrationError("That was a bad move.")

    # 4. Check if the precision of the UoM of the stock moves is enough
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
    assert cr.rowcount == 0

    return fixed_moves

def migrate(cr, version):
    # count moves
    cr.execute("SELECT count(*) FROM stock_move")
    moves_count, = cr.fetchone()
    if not moves_count:
        return

    # fix moves
    fixed_moves = fix_moves(cr)

    # allow 1% of error, maybe it should be increased
    if (float(fixed_moves) / float(moves_count)) > 0.015:
        raise util.MigrationError(
            "There is probably something wrong with the stock moves of the "
            "databases. Bad stock moves: %d/%d (%d%%)"
            % (fixed_moves, moves_count,
               (float(fixed_moves) / float(moves_count) * 100.0)))

    assert fix_moves(cr) == 0, "The code of fix_moves() is probably broken. "
