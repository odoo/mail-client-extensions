from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_contract_salary_payroll.hr_contract_salary_resume_view_search_inherit")
    util.remove_view(cr, "hr_contract_salary_payroll.hr_contract_view_form")
