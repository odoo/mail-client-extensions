# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "project_task", "sale_order_id", "int4")
    cr.execute("""
        UPDATE project_task t
          SET sale_order_id = l.order_id
         FROM sale_order_line l
        WHERE t.sale_line_id = l.id
    """)

    util.remove_field(cr, "sale.order", "project_project_id")
    util.create_column(cr, "sale_order_line", "project_id", "int4")
    # XXX verify with jem
    cr.execute("UPDATE sale_order_line SET project_id=NULL WHERE task_id IS NULL")
    cr.execute("""
        UPDATE sale_order_line l
           SET project_id = t.project_id
          FROM project_task t
         WHERE l.task_id = t.id
    """)

    util.remove_record(cr, "sale_timesheet.menu_timesheet_report_cost_revenue")
    util.remove_record(cr, "sale_timesheet.timesheet_action_report_cost_revenue_form")
    util.remove_record(cr, "sale_timesheet.timesheet_action_report_cost_revenue_tree")
    util.remove_record(cr, "sale_timesheet.timesheet_action_report_cost_revenue_pivot")
    util.remove_record(cr, "sale_timesheet.timesheet_action_report_cost_revenue")

    util.remove_view(cr, "sale_timesheet.hr_timesheet_employee_extd_form")
