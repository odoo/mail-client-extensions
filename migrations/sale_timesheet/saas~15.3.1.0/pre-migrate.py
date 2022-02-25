# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.change_field_selection_values(
        cr,
        "product.template",
        "service_policy",
        {
            "ordered_timesheet": "ordered_prepaid",
        },
    )
    util.remove_view(cr, "sale_timesheet.project_profitability_report_view_pivot")
    util.remove_view(cr, "sale_timesheet.project_profitability_report_view_graph")
    util.remove_view(cr, "sale_timesheet.project_profitability_report_view_tree")
    util.remove_view(cr, "sale_timesheet.project_profitability_report_view_search")
    util.remove_record(cr, "sale_timesheet.ir_filter_project_profitability_report_costs_and_revenues")
    util.remove_model(cr, "project.profitability.report")
