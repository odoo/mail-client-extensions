# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "industry_fsm_sale"):
        util.move_field_to_module(cr, "project.task", "invoice_count", "sale_project", "industry_fsm_sale")
    else:
        util.remove_field(cr, "project.task", "invoice_count")
    util.create_column(cr, "project_project", "allow_billable", "boolean", default=False)
    util.move_field_to_module(cr, "project.project", "allow_billable", "sale_timesheet", "sale_project")
    util.move_field_to_module(cr, "product.template", "service_policy", "sale_timesheet", "sale_project")
