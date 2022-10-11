# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "stock_enterprise.stock_report_view_grid")
    util.remove_view(cr, "stock_enterprise.stock_report_dashboard_view")

    util.rename_xmlid(
        cr,
        "stock_enterprise.stock_report_dashboard_action",
        "stock_enterprise.stock_report_action_performance",
    )

    util.remove_record(cr, "stock_enterprise.stock.report_stock_quantity_action_product")
    util.remove_record(cr, "stock_enterprise.stock.report_stock_quantity_action")
