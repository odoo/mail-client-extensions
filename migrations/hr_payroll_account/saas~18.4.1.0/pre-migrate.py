from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_payroll_account.hr_contract_view_form")
