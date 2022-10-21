# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "sale.order.line", "price_reduce")
    # sale_enterprise views, xmlids renamed by merge_module
    util.remove_view(cr, "sale.sale_report_view_pivot")
    util.remove_view(cr, "sale.view_order_product_search_inherit")
    util.remove_field(cr, "sale.report", "avg_days_to_confirm")
