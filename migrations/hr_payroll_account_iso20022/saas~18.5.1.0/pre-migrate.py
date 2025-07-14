from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_payroll_account_iso20022.hr_payslip_run_view_form")
