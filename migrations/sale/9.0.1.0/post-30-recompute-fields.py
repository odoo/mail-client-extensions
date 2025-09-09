# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # If slow, see below for a way to bootstrap these fields using a specific upgrade script
    # https://github.com/odoo/migration-scripts/commit/f4caab2e581d87d03a6f3d0399686dc4a411ad2b#diff-2caba28fcd819ffa2dd5b55d57c96ad3
    fields = ["price_tax", "price_subtotal", "price_total"]
    query = "SELECT id FROM sale_order_line WHERE price_total IS NULL ORDER BY product_id"
    util.recompute_fields(cr, "sale.order.line", fields, chunk_size=512, query=query)
    cr.execute(
        "UPDATE sale_order_line SET price_reduce=price_subtotal/product_uom_qty WHERE COALESCE(product_uom_qty,0)!=0"
    )
    cr.execute("UPDATE sale_order_line SET price_reduce=0 WHERE product_uom_qty=0")
