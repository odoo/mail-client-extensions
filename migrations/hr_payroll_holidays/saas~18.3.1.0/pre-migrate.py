from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_payroll_holidays.view_hr_leave_allocation_inherit_filter")
