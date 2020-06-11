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

    # Moved field from l10n_be_hr_payroll -> hr_contract_salary
    util.move_field_to_module(cr, "hr.contract", "final_yearly_costs", "l10n_be_hr_payroll", "hr_contract_salary")

    # Renamed field
    util.rename_field(cr, "generate.simulation.link", "vehicle_id", "car_id")

    # Created field
    util.create_column(cr, "hr_contract", "holidays", "float8")

    # Fields spouse_net_revenue/spouse_other_net_revenue
    # The selection for the fields spouse_fiscal_status has moved from
    # spouse_fiscal_status = fields.Selection([
    #     ('without income', 'Without Income'),
    #     ('with income', 'With Income')
    # To
    #     ('without_income', 'Without Income'),
    #     ('high_income', 'With High income'),
    #     ('low_income', 'With Low Income'),
    #     ('low_pension', 'With Low Pensions'),
    #     ('high_pension', 'With High Pensions')
    # Here are the different use cases
    # 1/ spouse_net_revenue == 0 and spouse_other_net_revenue == 0 --> without_income
    # 2/ 0 < spouse_net_revenue <= 233 --> low_income
    # 3/ spouse_net_revenue > 233 --> high_income
    # 4/ spouse_net_revenue == 0 and 0 < spouse_other_net_revenue <= 466 --> low_pension
    # 5/ spouse_net_revenue == 0 and spouse_other_net_revenue > 466 --> high_pension

    cr.execute(
        """
        UPDATE hr_employee
        SET spouse_fiscal_status =
            CASE
                WHEN
                    (spouse_net_revenue = 0
                    OR spouse_net_revenue IS NULL)
                    AND (spouse_other_net_revenue = 0
                    OR spouse_other_net_revenue IS NULL)
                    THEN 'without_income'
                WHEN
                    spouse_net_revenue != 0
                    AND spouse_net_revenue <= 233
                    THEN 'low_income'
                WHEN
                    spouse_net_revenue > 233
                    THEN 'high_income'
                WHEN
                    (spouse_net_revenue = 0
                    OR spouse_net_revenue IS NULL)
                    AND spouse_other_net_revenue != 0
                    AND spouse_other_net_revenue <= 466
                    THEN 'low_pension'
                WHEN
                    (spouse_net_revenue = 0
                    OR spouse_net_revenue IS NULL)
                    AND spouse_other_net_revenue > 466
                    THEN 'high_pension'
                ELSE 'without_income'
            END"""
    )

    # Removed fields
    removed_fields = {
        "generate.simulation.link": ["new_car_model_id"],
        "hr.contract": ["country_code"],
        "hr.employee": ["spouse_other_net_revenue", "spouse_net_revenue"],
        "res.users": ["spouse_other_net_revenue", "spouse_net_revenue"],
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
