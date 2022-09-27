# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    # removed record
    util.remove_record(cr, "sale_enterprise.sale_report_action_dashboard")
    util.remove_record(cr, "sale_enterprise.sale_report_action_dashboard_dashboard")
    util.remove_record(cr, "sale_enterprise.sale_report_action_dashboard_pivot")
    util.remove_record(cr, "sale_enterprise.sale_report_action_dashboard_graph")
    util.remove_record(cr, "sale_enterprise.menu_sale_report_dashboard")

    # removed view
    util.remove_view(cr, "sale_enterprise.sale_report_view_dashboard")
