# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("""
        UPDATE purchase_order_line l
           SET product_uom_qty = l.product_qty
          FROM product_product p, product_template t
         WHERE p.id = l.product_id
           AND t.id = p.product_tmpl_id
           AND t.uom_id = l.product_uom
    """)
    cr.execute("SELECT id FROM purchase_order_line WHERE product_uom_qty IS NULL")
    ids = [l[0] for l in cr.fetchall()]
    util.recompute_fields(cr, "purchase.order.line", ["product_uom_qty"], ids=ids)
