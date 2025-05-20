from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_contract_salary_holidays.hr_contract_view_form")
