# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "purchase_order_line", "sale_order_id", "int4")
    if util.module_installed(cr, "stock_dropshipping"):
        util.move_field_to_module(cr, "purchase.order.line", "sale_line_id", "stock_dropshipping", "sale_purchase")
        cr.execute(
            """
            UPDATE purchase_order_line p
            SET sale_order_id=s.order_id
            FROM sale_order_line s
            WHERE s.id=p.sale_line_id
        """
        )
