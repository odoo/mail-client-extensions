from odoo.upgrade import util
from odoo.upgrade.util.hr_payroll import remove_salary_rule


def migrate(cr, version):
    columns = [
        "l10n_ch_canton",
        "l10n_ch_tax_scale",
        "l10n_ch_municipality",
        "l10n_ch_religious_denomination",
        "l10n_ch_church_tax",
        "l10n_ch_marital_from",
        "l10n_ch_spouse_sv_as_number",
        "l10n_ch_spouse_work_canton",
        "l10n_ch_spouse_work_start_date",
        "l10n_ch_has_withholding_tax",
        "l10n_ch_residence_category",
    ]
    # l10n_ch_hr_payroll_elm_transmission is merged into l10n_ch_hr_payroll
    # Those fields could not exist if latter module wasn't installed
    if util.column_exists(cr, "hr_contract", "l10n_ch_laa_group"):
        columns.extend(
            [
                "l10n_ch_po_box",
                "l10n_ch_no_nationality",
                "l10n_ch_tax_scale_type",
                "l10n_ch_pre_defined_tax_scale",
                "l10n_ch_open_tax_scale",
                "l10n_ch_tax_specially_approved",
                "l10n_ch_concubinage",
                "l10n_ch_spouse_first_name",
                "l10n_ch_spouse_last_name",
                "l10n_ch_spouse_birthday",
                "l10n_ch_spouse_street",
                "l10n_ch_spouse_zip",
                "l10n_ch_spouse_city",
                "l10n_ch_spouse_country_id",
                "l10n_ch_spouse_revenues",
                "l10n_ch_spouse_work_end_date",
                "l10n_ch_spouse_residence_canton",
                "l10n_ch_cross_border_commuter",
                "l10n_ch_foreign_tax_id",
                "l10n_ch_cross_border_start",
                "l10n_ch_relationship_ceo",
                "l10n_ch_other_employment",
                "l10n_ch_total_activity_type",
                "l10n_ch_other_activity_percentage",
                "l10n_ch_other_activity_gross",
                "l10n_ch_working_days_in_ch",
                "l10n_ch_residence_type",
                "l10n_ch_weekly_residence_canton",
                "l10n_ch_weekly_residence_municipality",
                "l10n_ch_weekly_residence_address_street",
                "l10n_ch_weekly_residence_address_city",
                "l10n_ch_weekly_residence_address_zip",
                "l10n_ch_flex_profiling",
            ]
        )
    move_columns = util.import_script("hr/saas~18.4.1.1/post-migrate.py").move_columns
    move_columns(cr, employee_columns=columns)

    if util.table_exists(cr, "l10n_ch_lpp_insurance_line"):
        util.rename_field(cr, "l10n.ch.lpp.mutation", "contract_id", "version_id")
        util.rename_field(cr, "l10n.ch.hr.contract.wage", "contract_id", "version_id")
        util.rename_field(cr, "l10n.ch.swiss.wage.component", "contract_id", "version_id")

    util.remove_inherit_from_model(cr, "hr.salary.rule", "mail.thread")

    util.remove_model(cr, "l10n_ch.hr.payroll.employee.gender.wizard.line")
    util.remove_model(cr, "l10n_ch.hr.payroll.employee.gender.wizard")
    util.remove_model(cr, "l10n.ch.is.report.line")
    util.remove_model(cr, "ch.yearly.report.line")

    util.remove_field(cr, "l10n.ch.compensation.fund", "insurance_company")
    util.remove_field(cr, "l10n.ch.sickness.insurance", "insurance_company_address_id")
    util.remove_field(cr, "l10n.ch.sickness.insurance", "insurance_company")
    util.remove_field(cr, "l10n.ch.additional.accident.insurance", "insurance_company_address_id")
    util.remove_field(cr, "l10n.ch.additional.accident.insurance", "insurance_company")
    util.remove_field(cr, "l10n.ch.accident.insurance", "insurance_company_address_id")
    util.remove_field(cr, "l10n.ch.accident.insurance", "insurance_company")
    util.remove_field(cr, "l10n.ch.lpp.insurance", "insurance_company")
    util.remove_field(cr, "l10n.ch.lpp.insurance", "insurance_company_address_id")
    util.remove_field(cr, "l10n.ch.social.insurance", "insurance_company")
    util.remove_field(cr, "hr.employee.is.line", "correction_date")
    util.remove_field(cr, "hr.employee.is.line", "valid_as_of")
    util.remove_field(cr, "hr.employee", "l10n_ch_retirement_insurance_number")
    util.remove_field(cr, "l10n.ch.is.report", "report_line_ids")
    util.remove_field(cr, "l10n.ch.is.report", "work_location_ids")
    util.remove_field(cr, "l10n.ch.is.report", "currency_id")
    util.remove_field(cr, "l10n.ch.salary.certificate", "xml_filename")
    util.remove_field(cr, "l10n.ch.salary.certificate", "xml_file")
    util.remove_field(cr, "l10n.ch.salary.certificate", "currency_id")
    util.remove_field(cr, "ch.yearly.report", "report_line_ids")
    util.remove_field(cr, "ch.yearly.report", "currency_id")
    util.remove_field(cr, "l10n.ch.hr.contract.wage", "contract_state")

    util.remove_view(cr, "l10n_ch_hr_payroll.l10n_ch_is_report_view_tree")
    util.remove_view(cr, "l10n_ch_hr_payroll.l10n_ch_salary_certificate_view_tree")
    util.remove_view(cr, "l10n_ch_hr_payroll.l10n_be_individual_account_view_form")
    util.remove_view(cr, "l10n_ch_hr_payroll.l10n_ch_insurance_report_view_tree")
    util.remove_view(cr, "l10n_ch_hr_payroll.l10n_ch_insurance_report_view_form")
    util.remove_view(cr, "l10n_ch_hr_payroll.insurance_yearly_report")
    util.remove_view(cr, "l10n_ch_hr_payroll.l10n_ch_hr_employee_children_view_form")
    util.remove_view(cr, "l10n_ch_hr_payroll.l10n_ch_hr_employee_children_view_tree")
    util.remove_view(cr, "l10n_ch_hr_payroll.report_light_payslip_ch_lang")
    util.remove_view(cr, "l10n_ch_hr_payroll.report_light_payslip_ch")
    util.remove_view(cr, "l10n_ch_hr_payroll.report_payslip_ch_lang")
    util.remove_view(cr, "l10n_ch_hr_payroll.report_payslip_ch")
    util.remove_view(cr, "l10n_ch_hr_payroll.view_l10n_ch_tax_rate_import_wizard_inherit")
    util.remove_view(cr, "l10n_ch_hr_payroll.hr_payslip_line_view_search")
    util.remove_view(cr, "l10n_ch_hr_payroll.hr_payslip_line_view_pivot")
    util.remove_view(cr, "l10n_ch_hr_payroll.hr_payslip_run_form")
    util.remove_view(cr, "l10n_ch_hr_payroll.hr_employee_view_swissdec_form")

    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_other_fees")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_car_fees")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_representation_fees")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_other_expense")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_nightly_expense")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_lunch_expense")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_car_expense")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_family_allowance")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_flat_expatriate_costs")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_effective_expatriate_costs")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_travel_expense")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_employer_lpp_compensation_rachat")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_employer_lpp_compensation")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_cash_advantage_correction")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_benefits_in_kind_correction")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_restreint_private_share_service_car")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_fak_company")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_fak")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_withholding_tax")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_is_correction")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_is_rate")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_is_salary_dt")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_is_salary_dt_periodic")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_is_salary_dt_aperiodic")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_is_salary")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_is_salary_dt_ap")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_is_salary_dt_p")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_is_base")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_lpp_comp")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_lpp_redemption")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_lpp")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_optional_ijm")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_ijm_comp_2")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_ijm_comp_1")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_ijm_2")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_ijm_1")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_ijm_salary_2")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_ijm_salary_1")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_ijm_salary_min_2")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_ijm_salary_min_1")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_ijm_salary_max_2")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_ijm_salary_max_1")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_ijm_base")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_optional_laac")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_laac_comp_2")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_laac_comp_1")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_laac_2")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_laac")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_laac_salary_2")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_laac_salary_1")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_laac_salary_min_2")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_laac_salary_min_1")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_laac_salary_max_2")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_laac_salary_max_1")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_laac_base")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_optional_aanp")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_aanp_comp")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_aap_comp")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_aanp")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_laa_salary_2")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_laa_salary_max")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_laa_base")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_ac_open")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_compl_ac_comp")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_compl_ac")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_acc_salary")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_acc_salary_max")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_ac_comp")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_ac")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_ac_salary")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_ac_salary_max")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_ac_base")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_avs_comp")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_avs")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_avs_salary_retired")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_avs_salary")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_avs_open")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_avs_franchise_non_imp")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_avs_franchise")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_avs_base")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_gross_comp")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_marriage_allowance")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_birth_allowance")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_professional_training_allowance")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_child_allowance_payment")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_child_allowance")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_carence_rht_itp")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_indemnite_chomage")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_death_allowance")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_rht_itp_ded")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_indemnite_perte_gain")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_indemnity_maternity")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_third_party_correction")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_indemnity_illness")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_indemnity_accident")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_annuities_ai")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_indemnity_ai")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_military_wage")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_indemnity_apg")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_perfecting")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_third_pill_a")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_third_pill_b")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_optional_cm")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_optional_lpp_redemption")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_optional_lpp")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_option_collab")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_action_collab")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_tax_part_fees")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_rental_housing")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_company_car_employee")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_free_housing")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_free_room")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_free_meals")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_ca_fee")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_pension_capital")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_accident_wage")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_sick_wage")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_sev_pay")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_jubilee_gift")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_commission")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_imp_bonus")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_special_indemnity")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_bonus")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_14th_month")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_previous_year_bonus")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_gratification")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_thirteen_month")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_thirteen_month_provision")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_departure_time_off")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_vacation_payment")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_public_holiday_allowance")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_holiday_allowance")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_advance")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_night_allowance")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_sunday_allowance")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_on_call_alw")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_team_work")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_overtime_125")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_overtime_100")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_overtime_after_departure")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_house_allowance")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_func_allowance")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_fee")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_basic_lesson")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_basic_hourly")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_basic_correction")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_ch_days")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_worked_days")
    remove_salary_rule(cr, "l10n_ch_hr_payroll.l10n_ch_employees_as_days")
    util.delete_unused(cr, "l10n_ch_hr_payroll.hr_payroll_structure_ch_employee_salary")

    util.remove_model(cr, "l10n.ch.hr.payslip.montlhy.wizard")
    util.remove_menus(
        cr,
        [
            util.ref(cr, "l10n_ch_hr_payroll.menu_l10n_ch_hr_payslip_monthly_wizard"),
            util.ref(cr, "l10n_ch_hr_payroll.menu_hr_payroll_employees_swissdec_root"),
        ],
    )
