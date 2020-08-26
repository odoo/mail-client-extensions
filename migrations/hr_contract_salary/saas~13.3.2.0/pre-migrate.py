# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

    # Moved fields from hr_contract_salary -> l10n_be_hr_contract_salary
    moved_fields = {
        "generate.simulation.link": ["customer_relation", "contract_type", "new_car", "vehicle_id"],
        "hr.employee": ["internet_invoice", "sim_card", "mobile_invoice", "driving_license", "id_card"],
        "hr.contract": ["internet_invoice", "sim_card", "mobile_invoice", "driving_license", "id_card"],
    }
    for model, fields in moved_fields.items():
        for field in fields:
            util.move_field_to_module(cr, model, field, "hr_contract_salary", "l10n_be_hr_contract_salary")

    # Moved fields from l10n_be_hr_payroll -> hr_contract_salary
    fields = """
        holidays
        wage_with_holidays
        final_yearly_costs
        monthly_yearly_costs
    """
    for field in util.splitlines(fields):
        util.move_field_to_module(cr, "hr.contract", field, "l10n_be_hr_payroll", "hr_contract_salary")

    util.move_field_to_module(
        cr, "hr.contract.employee.report", "final_yearly_costs", "l10n_be_hr_payroll", "hr_contract_salary"
    )

    util.create_column(cr, "hr_contract", "holidays", "float8")

    # Renamed field
    util.rename_field(cr, "generate.simulation.link", "vehicle_id", "car_id")

    # Removed fields
    removed_fields = {
        "generate.simulation.link": ["new_car_model_id"],
        "hr.contract": ["country_code"],
    }
    for model, fields in removed_fields.items():
        for field in fields:
            util.remove_field(cr, model, field)

    # Demo data
    moved_data = """
        hr_department_rdbe
        job_developer_belgium
        employee_max
        res_partner_laurie_poiret
        user_laurie_poiret
        res_partner_laurie_poiret_work_address
        res_partner_bank_account_laurie_poiret
        hr_employee_laurie_poiret
        fleet_vehicle_audi_a3_laurie_poiret
        fleet_vehicle_log_contract_audi_a3_laurie_poiret
        hr_contract_cdi_experienced_developer
        hr_contract_cdi_laurie_poiret
        hr_employee_laurie_poiret
    """
    eb = util.expand_braces

    if util.module_installed(cr, "l10n_be_hr_contract_salary"):
        for data in util.splitlines(moved_data):
            util.rename_xmlid(cr, *eb(f"{{hr_contract_salary,l10n_be_hr_contract_salary}}.{data}"))
        # view
        util.rename_xmlid(cr, *eb("{hr_contract_salary,l10n_be_hr_contract_salary}.hr_employee_view_form"))
    else:
        for data in util.splitlines(moved_data):
            util.remove_record(cr, f"hr_contract_salary.{data}")
        util.remove_view(cr, "hr_contract_salary.hr_employee_view_form")

    util.remove_view(cr, "hr_contract_salary.assets_tests")
