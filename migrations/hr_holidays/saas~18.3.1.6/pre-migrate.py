from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_leave_type", "country_id", "int4")

    cr.execute(
        """
        UPDATE hr_leave_type hlt
           SET country_id = rp.country_id
          FROM res_company AS rc
          JOIN res_partner AS rp
            ON rp.id = rc.partner_id
         WHERE hlt.company_id = rc.id
        """
    )

    # Move leave types
    leave_type_by_country = {
        "none": {
            "holiday_status_cl": "leave_type_paid_time_off",
            "holiday_status_sl": "leave_type_sick_time_off",
            "holiday_status_comp": "leave_type_compensatory_days",
            "holiday_status_unpaid": "leave_type_unpaid",
        },
        "ae": {
            "uae_sick_leave_50_leave_type": "l10n_ae_leave_type_sick_leave_50",
            "uae_sick_leave_0_leave_type": "l10n_ae_leave_type_sick_leave_0",
        },
        "be": {
            "holiday_type_small_unemployment": "l10n_be_leave_type_small_unemployment",
            "holiday_type_maternity": "l10n_be_leave_type_maternity",
            "holiday_type_unpredictable": "l10n_be_leave_type_unpredictable",
            "holiday_type_training": "l10n_be_leave_type_training",
            "holiday_type_extra_legal": "l10n_be_leave_type_extra_legal",
            "holiday_type_recovery": "l10n_be_leave_type_recovery",
            "holiday_type_european": "l10n_be_leave_type_european",
            "holiday_type_credit_time": "l10n_be_leave_type_credit_time",
            "holiday_status_work_accident": "l10n_be_leave_type_work_accident",
            "holiday_type_strike": "l10n_be_leave_type_strike",
        },
        "hk": {
            "holiday_type_hk_annual_leave": "l10n_hk_leave_type_annual_leave",
            "holiday_type_hk_compensation_leave": "l10n_hk_leave_type_compensation_leave",
            "holiday_type_hk_sick_leave": "l10n_hk_leave_type_sick_leave",
            "holiday_type_hk_sick_leave_80": "l10n_hk_leave_type_sick_leave_80",
            "holiday_type_hk_unpaid_leave": "l10n_hk_leave_type_unpaid_leave",
            "holiday_type_hk_marriage_leave": "l10n_hk_leave_type_marriage_leave",
            "holiday_type_hk_maternity_leave": "l10n_hk_leave_type_maternity_leave",
            "holiday_type_hk_maternity_leave_80": "l10n_hk_leave_type_maternity_leave_80",
            "holiday_type_hk_paternity_leave": "l10n_hk_leave_type_paternity_leave",
            "holiday_type_hk_compassionate_leave": "l10n_hk_leave_type_compassionate_leave",
            "holiday_type_hk_examination_leave": "l10n_hk_leave_type_examination_leave",
        },
        "id": {
            "holiday_type_id_annual_leave": "l10n_id_leave_type_annual_leave",
            "holiday_type_id_sick_leave": "l10n_id_leave_type_sick_leave",
            "holiday_type_id_unpaid_leave": "l10n_id_leave_type_unpaid_leave",
            "holiday_type_id_marriage_leave": "l10n_id_leave_type_marriage_leave",
            "holiday_type_id_maternity_leave": "l10n_id_leave_type_maternity_leave",
            "holiday_type_id_paternity_leave": "l10n_id_leave_type_paternity_leave",
            "holiday_type_id_bereavement_leave": "l10n_id_leave_type_bereavement_leave",
        },
        "lu": {
            "holiday_status_situational_unemployment": "l10n_lu_leave_type_situational_unemployment",
        },
        "mx": {
            "holiday_type_work_risk_imss": "l10n_mx_leave_type_work_risk_imss",
            "holiday_type_maternity_imss": "l10n_mx_leave_type_maternity_imss",
            "holiday_type_disability_due_to_illness_imss": "l10n_mx_leave_type_disability_due_to_illness_imss",
        },
        "sk": {
            "hr_leave_type_maternity": "l10n_sk_leave_type_maternity",
        },
    }

    for country, xmlids in leave_type_by_country.items():
        module_name = "hr_holidays" if country == "none" else f"l10n_{country}_hr_payroll"
        for old, new in xmlids.items():
            old_xmlid = f"{module_name}.{old}"
            new_xmlid = f"hr_holidays.{new}"
            util.rename_xmlid(cr, old_xmlid, new_xmlid)

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("{hr_contract_salary,hr}_holidays.holiday_status_eto"))
    util.rename_xmlid(cr, *eb("hr_holidays{_attendance,}.holiday_status_extra_hours"))
    util.rename_xmlid(cr, *eb("{l10n_ch_hr_payroll_elm_transmission,hr_holidays}.l10n_ch_swissdec_unpaid_lt"))
    util.rename_xmlid(cr, *eb("{l10n_ch_hr_payroll_elm_transmission,hr_holidays}.l10n_ch_swissdec_illness_lt"))
    util.rename_xmlid(cr, *eb("{l10n_ch_hr_payroll_elm_transmission,hr_holidays}.l10n_ch_swissdec_accident_lt"))
    util.rename_xmlid(cr, *eb("{l10n_ch_hr_payroll_elm_transmission,hr_holidays}.l10n_ch_swissdec_maternity_lt"))
    util.rename_xmlid(cr, *eb("{l10n_ch_hr_payroll_elm_transmission,hr_holidays}.l10n_ch_swissdec_military_lt"))
    util.rename_xmlid(
        cr, *eb("{l10n_ch_hr_payroll_elm_transmission,hr_holidays}.l10n_ch_swissdec_interruption_of_work_lt")
    )
