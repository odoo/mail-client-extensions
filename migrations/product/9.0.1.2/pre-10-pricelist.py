# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
from openerp.tools import float_round


def migrate(cr, version):
    # before 9.0, rules (items) was deactivable through pricelist.versions
    # Now that the whole pricelist that should be deactivated.
    # duplicate the pricelist to include all deactivated versions
    cr.execute("SELECT 1 FROM product_pricelist_version WHERE active=false")
    if cr.rowcount:
        columns = util.get_columns(cr, 'product_pricelist', ('id', 'active'))
        p_columns = ["p." + c for c in columns]
        util.create_column(cr, 'product_pricelist', '_tmp', 'integer')
        cr.execute("""
            WITH n AS (
                INSERT INTO product_pricelist(_tmp, active, {columns})
                     (SELECT p.id, false, {p_columns}
                       FROM product_pricelist p
                      WHERE p.id IN (SELECT pricelist_id as id
                                       FROM product_pricelist_version
                                      WHERE active = false
                                   GROUP BY pricelist_id)
                      )
                RETURNING _tmp as old, id as new
            )
            UPDATE product_pricelist_version v
               SET pricelist_id = n.new
              FROM n
             WHERE v.pricelist_id = n.old
               AND v.active = false
        """.format(columns=', '.join(columns), p_columns=', '.join(p_columns)))

        util.remove_column(cr, 'product_pricelist', '_tmp')

    # adapt product.pricelist.item
    cr.execute('ALTER TABLE product_pricelist_item RENAME COLUMN "base" TO "_base"')
    util.create_column(cr, 'product_pricelist_item', 'currency_id', 'integer')
    util.create_column(cr, 'product_pricelist_item', 'pricelist_id', 'integer')
    util.create_column(cr, 'product_pricelist_item', 'date_start', 'date')
    util.create_column(cr, 'product_pricelist_item', 'date_end', 'date')
    util.create_column(cr, 'product_pricelist_item', 'applied_on', 'varchar')
    util.create_column(cr, 'product_pricelist_item', 'base', 'varchar')
    util.create_column(cr, 'product_pricelist_item', 'compute_price', 'varchar')
    util.create_column(cr, 'product_pricelist_item', 'fixed_price', 'numeric')
    util.create_column(cr, 'product_pricelist_item', 'percent_price', 'numeric')

    cr.execute("DELETE FROM product_price_type WHERE field='list_price' RETURNING id")
    list_price_ids = [-2] + [x[0] for x in cr.fetchall()]

    cr.execute("DELETE FROM product_price_type WHERE field='standard_price' RETURNING id")
    standard_price_ids = [x[0] for x in cr.fetchall()]

    cr.execute("""UPDATE product_pricelist_item i
                     SET pricelist_id = v.pricelist_id,
                         date_start = v.date_start,
                         date_end = v.date_end,
                         applied_on = CASE WHEN i.product_id IS NOT NULL THEN '0_product_variant'
                                           WHEN i.product_tmpl_id IS NOT NULL THEN '1_product'
                                           WHEN i.categ_id IS NOT NULL THEN '2_product_category'
                                           ELSE '3_global'
                                       END,
                         base = CASE WHEN i._base = -1 THEN 'pricelist'
                                     WHEN i._base = ANY(%s) THEN 'list_price'
                                     WHEN i._base = ANY(%s) THEN 'standard_price'
                                     ELSE 'standard_price'
                                 END,
                         compute_price = CASE WHEN i._base = ANY(%s) THEN 'formula'
                                              ELSE 'fixed'
                                          END,
                         price_discount = i.price_discount * -100
                    FROM product_pricelist_version v
                   WHERE v.id = i.price_version_id
               """, [list_price_ids, standard_price_ids,
                     [-1] + list_price_ids + standard_price_ids,
                     ])

    cr.execute("""UPDATE product_pricelist_item i
                     SET currency_id = p.currency_id
                    FROM product_pricelist p
                   WHERE i.pricelist_id = p.id
    """)
    # The rules that used "pricetype" should be set as "fixed".
    # Create a rule per product that match the configuration
    ppt = {}
    cr.execute("""SELECT t.id, t.field, MIN(c.table_name)
                    FROM product_price_type t,
                         information_schema.columns c
                   WHERE c.column_name = t.field
                     AND c.table_name IN ('product_product', 'product_template')
                GROUP BY t.id, t.field, t.currency_id
    """)
    for pptid, field, table in cr.fetchall():
        ppt[pptid] = {
            'field': field,
            'table': table,
        }

    def apply_formula(price, discount, round_, surcharge, min_margin, max_margin):
        price_limit = price
        price = (price - (price * (discount / 100))) or 0.0
        if round_:
            price = float_round(price, precision_rounding=round_)
        if surcharge:
            price += surcharge
        if min_margin:
            price = max(price, price_limit + min_margin)
        if max_margin:
            price = min(price, price_limit + max_margin)
        return price

    columns = util.get_columns(
        cr,
        "product_pricelist_item",
        ("id", "product_id", "product_tmpl_id", "categ_id", "fixed_price", "applied_on"),
    )
    i_columns = ["i." + c for c in columns]

    cr.execute("""SELECT id, _base, product_id, product_tmpl_id, categ_id,
                         ARRAY [price_discount::float8, price_round::float8, price_surcharge::float8,
                                price_min_margin::float8, price_max_margin::float8] AS formula
                    FROM product_pricelist_item
                   WHERE compute_price = 'fixed'
               """)

    for rid, base, pid, tid, cid, formula in cr.fetchall():
        if base not in ppt:
            # unknown pricetype, cannot get the fixed price => delete the rule
            cr.execute("DELETE FROM product_pricelist_item WHERE id=%s", [rid])
            continue

        if pid:
            product_filter = '= %s'
            params = [pid]
        elif tid:
            product_filter = 'IN (SELECT id FROM product_product WHERE product_tmpl_id=%s)'
            params = [tid]
        elif cid:
            product_filter = """IN(SELECT pp.id
                                     FROM product_product pp
                                     JOIN product_template pt ON (pt.id=pp.product_tmpl_id)
                                     JOIN product_category pc ON (pc.id = pt.categ_id),
                                     product_category pc_ref
                                    WHERE pc_ref.id = %s
                                      AND pc.parent_left < pc_ref.parent_right
                                      AND pc.parent_left >= pc_ref.parent_left
                                  )
                             """
            params = [cid]
        else:
            # all products
            product_filter = 'IS NOT NULL'
            params = []

        t = 'p' if ppt[base]['table'] == 'product_product' else 't'
        cr.execute("""SELECT COALESCE({t}.{field}, 0), array_agg(p.id)
                        FROM product_product p
                        JOIN product_template t ON (t.id = p.product_tmpl_id)
                       WHERE p.id {product_filter}
                       GROUP BY 1
                       ORDER BY array_length(array_agg(p.id), 1)
                   """.format(t=t, field=ppt[base]['field'], product_filter=product_filter), params)
        data = cr.fetchall()
        if data:
            price, pids = data[0]
            price = apply_formula(price, *formula)
            # update current rule
            cr.execute("""UPDATE product_pricelist_item
                             SET fixed_price=%s,
                             product_id=%s, product_tmpl_id=NULL, categ_id=NULL,
                             applied_on='0_product_variant'
                           WHERE id=%s
                       """, [price, pids[0], rid])
            pids.pop(0)
            if not pids:
                data.pop(0)

        # copy the rest
        for price, pids in data:
            price = apply_formula(price, *formula)
            cr.execute("""
                INSERT INTO product_pricelist_item({columns}, fixed_price, product_id, applied_on)
                SELECT {i_columns}, %s, unnest(%s), '0_product_variant'
                  FROM product_pricelist_item i
                 WHERE i.id = %s
                       """.format(columns=','.join(columns), i_columns=','.join(i_columns)),
                       [price, pids, rid])

    # convert simple "100%" discount with surchage formula to "fixed" rule
    cr.execute("""
        UPDATE product_pricelist_item i
           SET compute_price = 'fixed',
               fixed_price = price_surcharge,
               price_surcharge = 0,
               price_discount = 0
         WHERE compute_price = 'formula'
           AND price_discount = 100
           AND price_round = 0
           AND price_min_margin = 0
           AND price_max_margin = 0
    """)
    # and simple discount formula (not based on another pricelist) to "percentage" rule
    cr.execute("""
        UPDATE product_pricelist_item i
           SET compute_price = 'percentage',
               percent_price = price_discount,
               price_discount = 0
         WHERE compute_price = 'formula'
           AND price_surcharge = 0
           AND price_round = 0
           AND price_min_margin = 0
           AND price_max_margin = 0
           AND base = 'list_price'
    """)

    # cleanup
    util.remove_column(cr, 'product_pricelist_item', 'name')    # now a computed field
    util.remove_column(cr, 'product_pricelist_item', '_base')
    util.remove_field(cr, 'product.pricelist.item', 'price_version_id')
    util.delete_model(cr, 'product.price.type')
    util.delete_model(cr, 'product.pricelist.type')
    util.delete_model(cr, 'product.pricelist.version')
