# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    # removed view
    util.remove_view(cr, "stock_enterprise.stock_report_dashboard_view")

    # renamed
    util.rename_xmlid(
        cr, "stock_enterprise.stock_report_dashboard_action", "stock_enterprise.stock_report_action_performance"
    )
