# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT sol.id
          FROM sale_order_line sol
         WHERE sol.qty_delivered_method = 'timesheet'
        """
    )
    ids = [row[0] for row in cr.fetchall()]
    util.recompute_fields(cr, "sale.order.line", ["purchase_price"], ids=ids)
