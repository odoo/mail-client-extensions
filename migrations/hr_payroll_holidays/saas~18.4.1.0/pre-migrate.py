from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_payroll_holidays.hr_payslip_run_view_tree")
