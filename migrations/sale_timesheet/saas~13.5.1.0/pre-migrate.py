# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "sale.advance.payment.inv", "date_invoice_timesheet")
    util.create_column(cr, "sale_advance_payment_inv", "date_start_invoice_timesheet", "date")
    util.create_column(cr, "sale_advance_payment_inv", "date_end_invoice_timesheet", "date")

    util.remove_field(cr, "project.create.sale.order", "product_id")
    util.remove_field(cr, "project.create.sale.order", "price_unit")
    util.remove_field(cr, "project.create.sale.order", "currency_id")
    util.remove_field(cr, "project.create.sale.order", "billable_type")
    util.create_column(cr, "project_create_sale_order", "link_selection", "varchar")
    util.create_column(cr, "project_create_sale_order", "sale_order_id", "int4")
    util.create_column(cr, "project_create_sale_order_line", "sale_line_id", "int4")

    util.create_column(cr, "project_task_create_sale_order", "link_selection", "varchar")
    util.create_column(cr, "project_task_create_sale_order", "sale_order_id", "int4")
    util.create_column(cr, "project_task_create_sale_order", "sale_line_id", "int4")

    util.create_column(cr, "project_project", "bill_type", "varchar")
    util.create_column(cr, "project_project", "pricing_type", "varchar")
    cr.execute(
        """
    UPDATE project_project
       SET bill_type = 'customer_task'
     WHERE allow_billable IS TRUE AND billable_type = 'no'
        """
    )
    cr.execute(
        """
    UPDATE project_project
       SET bill_type = 'customer_project', pricing_type = 'employee_rate'
     WHERE allow_billable IS TRUE AND billable_type = 'employee_rate'
        """
    )
    cr.execute(
        """
    UPDATE project_project
       SET bill_type = 'customer_project', pricing_type = 'fixed_rate'
     WHERE allow_billable IS TRUE AND billable_type = 'task_rate'
        """
    )
    util.remove_field(cr, "project.project", "billable_type")

    util.remove_field(cr, "project.task", "billable_type")
    util.create_column(cr, "project_task", "non_allow_billable", "boolean")
    util.create_column(cr, "project_task", "timesheet_product_id", "int4")

    util.create_column(cr, "account_analytic_line", "non_allow_billable", "boolean")
    util.create_column(cr, "project_sale_line_employee_map", "timesheet_product_id", "int4")
