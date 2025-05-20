from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "hr_work_entry.overtime_work_entry_type", "hr_work_entry.work_entry_type_overtime")

    # Move work entry types
    work_entry_type_by_country = {
        "none": {
            "work_entry_type_leave": "work_entry_type_leave",
            "work_entry_type_compensatory": "work_entry_type_compensatory",
            "work_entry_type_home_working": "work_entry_type_home_working",
            "work_entry_type_unpaid_leave": "work_entry_type_unpaid_leave",
            "work_entry_type_sick_leave": "work_entry_type_sick_leave",
            "work_entry_type_legal_leave": "work_entry_type_legal_leave",
        },
        "ae": {
            "uae_sick_leave_50_entry_type": "l10n_ae_work_entry_type_sick_leave_50",
            "uae_sick_leave_0_entry_type": "l10n_ae_work_entry_type_sick_leave_0",
        },
        "au": {
            "l10n_au_work_entry_paid_time_off": "l10n_au_work_entry_type_paid_time_off",
            "l10n_au_work_entry_long_service_leave": "l10n_au_work_entry_type_long_service_leave",
            "l10n_au_work_entry_personal_leave": "l10n_au_work_entry_type_personal_leave",
            "l10n_au_work_entry_type_other": "l10n_au_work_entry_type_other",
            "l10n_au_work_entry_type_parental": "l10n_au_work_entry_type_parental",
            "l10n_au_work_entry_type_compensation": "l10n_au_work_entry_type_compensation",
            "l10n_au_work_entry_type_defence": "l10n_au_work_entry_type_defence",
            "l10n_au_work_entry_type_cash_out": "l10n_au_work_entry_type_cash_out",
            "l10n_au_work_entry_type_termination": "l10n_au_work_entry_type_termination",
            "l10n_au_work_entry_type_overtime_regular": "l10n_au_work_entry_type_overtime_regular",
            "l10n_au_work_entry_type_overtime_saturday": "l10n_au_work_entry_type_overtime_saturday",
            "l10n_au_work_entry_type_overtime_sunday": "l10n_au_work_entry_type_overtime_sunday",
            "l10n_au_work_entry_type_overtime_pto": "l10n_au_work_entry_type_overtime_pto",
            "l10n_au_work_entry_type_overtime_saturday_pto": "l10n_au_work_entry_type_overtime_saturday_pto",
            "l10n_au_work_entry_type_overtime_sunday_pto": "l10n_au_work_entry_type_overtime_sunday_pto",
        },
        "be": {
            "work_entry_type_bank_holiday": "l10n_be_work_entry_type_bank_holiday",
            "work_entry_type_solicitation_time_off": "l10n_be_work_entry_type_solicitation_time_off",
            "work_entry_type_unjustified_reason": "l10n_be_work_entry_type_unjustified_reason",
            "work_entry_type_small_unemployment": "l10n_be_work_entry_type_small_unemployment",
            "work_entry_type_economic_unemployment": "l10n_be_work_entry_type_economic_unemployment",
            "work_entry_type_corona": "l10n_be_work_entry_type_corona",
            "work_entry_type_maternity": "l10n_be_work_entry_type_maternity",
            "work_entry_type_paternity_company": "l10n_be_work_entry_type_paternity_company",
            "work_entry_type_paternity_legal": "l10n_be_work_entry_type_paternity_legal",
            "work_entry_type_unpredictable": "l10n_be_work_entry_type_unpredictable",
            "work_entry_type_training": "l10n_be_work_entry_type_training",
            "work_entry_type_training_time_off": "l10n_be_work_entry_type_training_time_off",
            "work_entry_type_flemish_training_time_off": "l10n_be_work_entry_type_flemish_training_time_off",
            "work_entry_type_long_sick": "l10n_be_work_entry_type_long_sick",
            "work_entry_type_breast_feeding": "l10n_be_work_entry_type_breast_feeding",
            "work_entry_type_medical_assistance": "l10n_be_work_entry_type_medical_assistance",
            "work_entry_type_youth_time_off": "l10n_be_work_entry_type_youth_time_off",
            "work_entry_type_recovery_additional": "l10n_be_work_entry_type_recovery_additional",
            "work_entry_type_additional_paid": "l10n_be_work_entry_type_additional_paid",
            "work_entry_type_notice": "l10n_be_work_entry_type_notice",
            "work_entry_type_phc": "l10n_be_work_entry_type_phc",
            "work_entry_type_extra_legal": "l10n_be_work_entry_type_extra_legal",
            "work_entry_type_part_sick": "l10n_be_work_entry_type_part_sick",
            "work_entry_type_recovery": "l10n_be_work_entry_type_recovery",
            "work_entry_type_european": "l10n_be_work_entry_type_european",
            "work_entry_type_credit_time": "l10n_be_work_entry_type_credit_time",
            "work_entry_type_parental_time_off": "l10n_be_work_entry_type_parental_time_off",
            "work_entry_type_simple_holiday_pay_variable_salary": "l10n_be_work_entry_type_simple_holiday_pay_variable_salary",
            "work_entry_type_work_accident": "l10n_be_work_entry_type_work_accident",
            "work_entry_type_partial_incapacity": "l10n_be_work_entry_type_partial_incapacity",
            "work_entry_type_strike": "l10n_be_work_entry_type_strike",
        },
        "ch": {
            "work_entry_type_bank_holiday": "l10n_ch_work_entry_type_bank_holiday",
        },
        "hk": {
            "work_entry_type_sick_leave_80": "l10n_hk_work_entry_type_sick_leave_80",
            "work_entry_type_compassionate_leave": "l10n_hk_work_entry_type_compassionate_leave",
            "work_entry_type_marriage_leave": "l10n_hk_work_entry_type_marriage_leave",
            "work_entry_type_examination_leave": "l10n_hk_work_entry_type_examination_leave",
            "work_entry_type_maternity_leave": "l10n_hk_work_entry_type_maternity_leave",
            "work_entry_type_maternity_leave_80": "l10n_hk_work_entry_type_maternity_leave_80",
            "work_entry_type_paternity_leave": "l10n_hk_work_entry_type_paternity_leave",
            "work_entry_type_statutory_holiday": "l10n_hk_work_entry_type_statutory_holiday",
            "work_entry_type_public_holiday": "l10n_hk_work_entry_type_public_holiday",
            "work_entry_type_weekend": "l10n_hk_work_entry_type_weekend",
        },
        "id": {
            "work_entry_type_bereavement_leave": "l10n_id_work_entry_type_bereavement_leave",
            "work_entry_type_marriage_leave": "l10n_id_work_entry_type_marriage_leave",
            "work_entry_type_maternity_leave": "l10n_id_work_entry_type_maternity_leave",
            "work_entry_type_paternity_leave": "l10n_id_work_entry_type_paternity_leave",
            "work_entry_type_public_holiday": "l10n_id_work_entry_type_public_holiday",
        },
        "lu": {
            "work_entry_type_situational_unemployment": "l10n_lu_work_entry_type_situational_unemployment",
        },
        "mx": {
            "l10n_mx_work_entry_type_work_risk_imss": "l10n_mx_work_entry_type_work_risk_imss",
            "l10n_mx_work_entry_type_maternity_imss": "l10n_mx_work_entry_type_maternity_imss",
            "l10n_mx_work_entry_type_disability_due_to_illness_imss": "l10n_mx_work_entry_type_disability_due_to_illness_imss",
            "l10n_mx_work_risk_imss": "l10n_mx_work_entry_type_work_risk_imss",
            "l10n_mx_maternity_imss": "l10n_mx_work_entry_type_maternity_imss",
            "l10n_mx_disability_due_to_illness_imss": "l10n_mx_work_entry_type_disability_due_to_illness_imss",
        },
        "sk": {
            "work_entry_type_sick_25": "l10n_sk_work_entry_type_sick_25",
            "work_entry_type_sick_55": "l10n_sk_work_entry_type_sick_55",
            "work_entry_type_sick_0": "l10n_sk_work_entry_type_sick_0",
            "work_entry_type_maternity": "l10n_sk_work_entry_type_maternity",
            "work_entry_type_parental_time_off": "l10n_sk_work_entry_type_parental_time_off",
        },
        "us": {
            "double_work_entry_type": "l10n_us_work_entry_type_double",
            "retro_overtime_work_entry_type": "l10n_us_work_entry_type_retro_overtime",
            "retro_regular_work_entry_type": "l10n_us_work_entry_type_retro_regular",
        },
    }

    for country, xmlids in work_entry_type_by_country.items():
        for old, new in xmlids.items():
            old_module = "hr_work_entry_contract" if country == "none" else f"l10n_{country}_hr_payroll"
            old_xmlid = f"{old_module}.{old}"
            new_xmlid = f"hr_work_entry.{new}"
            util.rename_xmlid(cr, old_xmlid, new_xmlid)

    # Module l10n_ch_hr_payroll_elm_transmission has been merged into l10n_ch_hr_payroll in 18.4
    # Could break on upgrade 18.0 -> 18.4
    if util.module_installed(cr, "l10n_ch_hr_payroll_elm_transmission"):
        transmission_module_name = "l10n_ch_hr_payroll_elm_transmission"
    else:
        transmission_module_name = "l10n_ch_hr_payroll"

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("{hr_payroll,hr_work_entry}.hr_work_entry_type_out_of_contract"))
    util.rename_xmlid(cr, *eb(f"{{{transmission_module_name},hr_work_entry}}.l10n_ch_swissdec_monthly_wt"))
    util.rename_xmlid(cr, *eb(f"{{{transmission_module_name},hr_work_entry}}.l10n_ch_swissdec_hourly_wt"))
    util.rename_xmlid(cr, *eb(f"{{{transmission_module_name},hr_work_entry}}.l10n_ch_swissdec_lesson_wt"))
    util.rename_xmlid(cr, *eb(f"{{{transmission_module_name},hr_work_entry}}.l10n_ch_swissdec_overtime_wt"))
    util.rename_xmlid(cr, *eb(f"{{{transmission_module_name},hr_work_entry}}.l10n_ch_swissdec_overtime_125_wt"))
    util.rename_xmlid(cr, *eb(f"{{{transmission_module_name},hr_work_entry}}.l10n_ch_swissdec_unpaid_wt"))
    util.rename_xmlid(cr, *eb(f"{{{transmission_module_name},hr_work_entry}}.l10n_ch_swissdec_illness_wt"))
    util.rename_xmlid(cr, *eb(f"{{{transmission_module_name},hr_work_entry}}.l10n_ch_swissdec_accident_wt"))
    util.rename_xmlid(cr, *eb(f"{{{transmission_module_name},hr_work_entry}}.l10n_ch_swissdec_maternity_wt"))
    util.rename_xmlid(cr, *eb(f"{{{transmission_module_name},hr_work_entry}}.l10n_ch_swissdec_military_wt"))
    util.rename_xmlid(cr, *eb(f"{{{transmission_module_name},hr_work_entry}}.l10n_ch_swissdec_illness_wt_hourly"))
    util.rename_xmlid(cr, *eb(f"{{{transmission_module_name},hr_work_entry}}.l10n_ch_swissdec_accident_wt_hourly"))
    util.rename_xmlid(cr, *eb(f"{{{transmission_module_name},hr_work_entry}}.l10n_ch_swissdec_maternity_wt_hourly"))
    util.rename_xmlid(cr, *eb(f"{{{transmission_module_name},hr_work_entry}}.l10n_ch_swissdec_military_wt_hourly"))
    util.rename_xmlid(cr, *eb(f"{{{transmission_module_name},hr_work_entry}}.l10n_ch_swissdec_interruption_wt"))
    util.rename_xmlid(
        cr, *eb("{l10n_be_hr_payroll_acerta.,hr_work_entry.l10n_be_}work_entry_type_small_unemployment_birth")
    )

    # also migrate demo to avoid errors on runbot upgrade builds with demo
    util.rename_xmlid(cr, *eb("hr_work_entry{_contract,}.work_entry_type_extra_hours"))
    util.rename_xmlid(cr, *eb("hr_work_entry{_contract,}.work_entry_type_long_leave"))
