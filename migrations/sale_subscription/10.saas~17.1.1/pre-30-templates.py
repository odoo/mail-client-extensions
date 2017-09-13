# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    T = util.env(cr)['product.template']
    util.create_column(cr, 'product_template', 'subscription_template_id', 'int4')
    cr.execute("""
        WITH tmpls (ptid, stid, others) AS (
            SELECT p.product_tmpl_id,
                   (array_agg(l.subscription_template_id order by l.subscription_template_id))[1] as stid,
                   (array_agg(l.subscription_template_id order by l.subscription_template_id))[2:array_length(array_agg(l.subscription_template_id), 1)] as others
              FROM sale_subscription_template_line l
              JOIN product_product p ON (p.id = l.product_id)
          GROUP BY p.product_tmpl_id
        ),
        _upd AS (
            UPDATE product_template
               SET subscription_template_id = t.stid
              FROM tmpls t
        )
        SELECT ptid, unnest(others)
          FROM tmpls
         WHERE array_length(others, 1) > 0
    """)
    for ptid, stid in cr.fetchall():
        nid = T.browse(ptid).copy().id
        cr.execute("UPDATE product_template SET subscription_template_id=%s WHERE id=%s", [stid, nid])

    util.delete_model(cr, 'sale.subscription.template.line')
