# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    util.move_field_to_module(cr, "project.project", "allow_billable", "sale_timesheet_enterprise", "sale_timesheet")
    util.move_field_to_module(cr, "project.task", "allow_billable", "sale_timesheet_enterprise", "sale_timesheet")
    util.move_model(cr, "project.task.create.sale.order", "sale_timesheet_enterprise", "sale_timesheet")
    util.rename_xmlid(cr, *eb("sale_timesheet{_enterprise,}.project_task_create_sale_order_view_form"))
    util.rename_xmlid(cr, *eb("sale_timesheet{_enterprise,}.project_task_action_multi_create_sale_order"))

    util.create_column(cr, "project_project", "allow_billable", "boolean")
    extra_cond = ""
    if util.column_exists(cr, "project_project", "timesheet_product_id"):
        # if `industry_fsm_sale` is installed, there is a constraint of presence of a product
        extra_cond = "AND timesheet_product_id IS NOT NULL"
    cr.execute(
        f"""
        UPDATE project_project p
           SET allow_billable = (
                    billable_type != 'no'
                AND (   sale_order_id IS NOT NULL
                     OR EXISTS(SELECT id FROM project_sale_line_employee_map WHERE project_id = p.id)
                )
                {extra_cond}
               )
         WHERE allow_billable IS NULL
    """
    )

    util.create_column(cr, "sale_advance_payment_inv", "date_invoice_timesheet", "date")
    util.create_column(cr, "sale_advance_payment_inv", "invoicing_timesheet_enabled", "boolean")

    util.remove_record(cr, "sale_timesheet.timesheet_filter_billing")
