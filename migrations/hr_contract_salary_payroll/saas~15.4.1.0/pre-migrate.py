# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr,
        "hr_contract_salary_payroll.hr_contract_salary_resume_net",
        "hr_contract_salary_payroll.hr_contract_salary_resume_net_employee",
    )
