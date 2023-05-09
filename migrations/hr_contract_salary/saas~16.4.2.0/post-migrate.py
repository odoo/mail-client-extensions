# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "hr_contract_salary.hr_contract_salary_personal_info_street")
    util.update_record_from_xml(cr, "hr_contract_salary.hr_contract_salary_personal_info_street2")
    util.update_record_from_xml(cr, "hr_contract_salary.hr_contract_salary_personal_info_city")
    util.update_record_from_xml(cr, "hr_contract_salary.hr_contract_salary_personal_info_zip")
    util.update_record_from_xml(cr, "hr_contract_salary.hr_contract_salary_personal_info_state_id")
    util.update_record_from_xml(cr, "hr_contract_salary.hr_contract_salary_personal_info_country")
    util.update_record_from_xml(cr, "hr_contract_salary.hr_contract_salary_personal_info_email")
    util.update_record_from_xml(cr, "hr_contract_salary.hr_contract_salary_personal_info_phone")
