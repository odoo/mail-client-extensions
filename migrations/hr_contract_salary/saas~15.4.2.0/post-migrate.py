# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "hr_contract_salary.hr_contract_salary_resume_rule_multi_company")
