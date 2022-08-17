# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.convert_field_to_html(cr, "hr.contract.salary.advantage", "description")
    util.create_column(cr, "hr_contract_salary_advantage", "show_name", "boolean", default=True)
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_transport_new_car")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_transport_public")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_transport_train")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_transport_private_car")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_transport_private_bike")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_transport_company_bike")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_insured_spouse")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_insured_children")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_insured_adults")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_hospital_insurance_note")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_ambulatory_insured_spouse")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_ambulatory_insured_children")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_ambulatory_insured_adults")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_ambulatory_insurance_note")
