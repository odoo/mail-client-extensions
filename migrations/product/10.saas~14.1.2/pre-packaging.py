# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'product_packaging', 'product_id', 'int4')
    util.create_column(cr, 'product_packaging', '_tmp', 'int4')
    cols = util.get_columns(cr, 'product_packaging', ('id', 'product_id', '_tmp'))

    k_cols = ",".join("k." + c for c in cols)
    cols = ",".join(cols)

    update_sol = ""
    if util.column_exists(cr, 'sale_order_line', 'product_packaging'):
        update_sol = """
            ,
            _update_sol AS (
                UPDATE sale_order_line l
                   SET product_packaging = d.id
                  FROM new_packs d
                 WHERE l.product_packaging = d._tmp
                   AND l.product_id = d.product_id
            )
        """
    # XXX also update stock.move and stock.quant ???

    cr.execute("""
        WITH pack_products AS (
            SELECT k.id as pack_id, array_agg(p.id order by p.id) as products
              FROM product_packaging k
              JOIN product_product p ON (p.product_tmpl_id = k.product_tmpl_id)
          GROUP BY pack_id
        ),
        upd_first AS (
              UPDATE product_packaging k
                 SET product_id = t.products[1]
                FROM pack_products t
               WHERE t.pack_id = k.id
        ),
        new_packs AS (
            INSERT INTO product_packaging({cols}, product_id, _tmp)
                 SELECT {k_cols}, unnest(t.products[2:array_length(t.products, 1)]), k.id
                   FROM product_packaging k
                   JOIN pack_products t ON (k.id = t.pack_id)
              RETURNING id, product_id, _tmp
        )
        {update_sol}
        SELECT 1
    """.format(**locals()))

    util.remove_field(cr, 'product.packaging', 'product_tmpl_id')
    util.remove_column(cr, 'product_packaging', '_tmp')
