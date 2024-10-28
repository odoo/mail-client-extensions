from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale_timesheet_enterprise.sale_timesheet_inherit_project_task_view_form")
