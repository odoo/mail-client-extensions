# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale_timesheet.view_hr_timesheet_pivot_view_per_invoice")
    util.remove_view(cr, "sale_timesheet.timesheet_view_pivot_revenue")
    util.remove_view(cr, "sale_timesheet.view_hr_timesheet_line_graph_groupby_invoice_type")
    for mode in "form kanban tree".split():
        util.remove_record(cr, f"sale_timesheet.timesheet_action_view_report_by_billing_rate_{mode}")
