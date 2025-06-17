from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "edit.billable.time.target", "job_title")
    util.remove_view(cr, "sale_timesheet_enterprise.hr_employee_public_form_view_inherit")
