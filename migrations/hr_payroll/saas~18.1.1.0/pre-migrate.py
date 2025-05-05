from odoo import models

from odoo.addons.hr_payroll.models import hr_salary_rule_category as _ignore  # noqa

from odoo.upgrade import util


class HrSalaryRuleCategory(models.Model):
    _inherit = "hr.salary.rule.category"
    _module = "hr_payroll"

    def _check_rule_category_country(self):
        pass


def migrate(cr, version):
    util.create_column(cr, "hr_salary_rule_category", "country_id", "int4")

    xmlids_by_country = {
        "au": [
            "rule_category_conditions_qualifications_duties",
            "rule_category_non_deductible_expense",
            "rule_category_deductible_expense",
            "rule_category_ordinary_on_call",
            "rule_category_non_ordinary_on_call",
            "rule_category_withholding",
            "rule_category_withholding_offsets",
            "rule_category_net_withholding",
            "rule_category_super_contribution",
            "rule_category_etp_base",
            "rule_category_tax_free_component",
            "rule_category_child_support_garnishee",
            "rule_category_child_support",
            "rule_category_salary_sacrifice",
            "rule_category_salary_sacrifice_total",
            "rule_category_ote",
            "rule_category_workplace_giving",
            "rule_category_extra_payments",
            "rule_category_benefits",
            "rule_category_return_to_work",
        ],
        "bd": [
            "rule_category_taxes",
            "rule_category_taxable",
            "rule_category_tax_credits",
        ],
        "be": [
            "hr_payroll_head_salary",
            "hr_payroll_head_onss",
            "hr_payroll_head_employment_bonus",
            "hr_payroll_head_div_impos",
            "hr_payroll_head_pp",
            "hr_payroll_head_div_net",
            "hr_payroll_head_child_alw",
            "hr_salary_rule_category_spec_soc_contribution",
            "hr_salary_rule_category_ip_part",
            "hr_salary_rule_category_gross_with_ip",
            "hr_payroll_head_dp",
            "hr_payroll_termination",
            "hr_payroll_termination_salary",
            "hr_payroll_notice_duration",
            "hr_payroll_termination_holidays_simple",
            "hr_payroll_termination_holidays_double",
            "hr_payroll_termination_holidays_double_basic",
            "hr_payroll_termination_holidays_additional_leave",
            "hr_payroll_termination_holidays",
            "hr_salary_rule_category_remuneration",
            "hr_salary_rule_category_owed_remuneration",
            "hr_salary_rule_category_onss_employer_detail",
            "hr_salary_rule_category_onss_employer",
            "hr_salary_rule_category_withholding_taxes_total",
            "hr_salary_rule_category_onss_total",
            "hr_salary_rule_category_m_onss_total",
            "hr_payroll_onss_restructuring",
            "salary_rule_category_commissions",
            "salary_rule_category_commissions_adjustment",
            "l10n_be_simple_december_category",
            "l10n_be_double_december_category",
            "l10n_be_double_december_category_gross",
            "hr_salary_rule_category_group_insurance",
            "hr_salary_rule_category_vouchers",
        ],
        "ch": [
            "hr_salary_rule_category_comp_part",
            "hr_salary_rule_category_caf",
            "hr_salary_rule_category_thirteen_month",
            "hr_salary_rule_category_avs_salary",
            "hr_salary_rule_category_ac_salary",
            "hr_salary_rule_category_acc_salary",
            "hr_salary_rule_category_aanp_salary",
            "hr_salary_rule_category_laac_salary",
            "hr_salary_rule_category_ijm_salary",
            "hr_salary_rule_category_avs_base",
            "hr_salary_rule_category_avs_franchise",
            "hr_salary_rule_category_avs_franchise_non_imp",
            "hr_salary_rule_category_avs_salary_retired",
            "hr_salary_rule_category_avs_open",
            "hr_salary_rule_category_ac_base",
            "hr_salary_rule_category_ac_threshold",
            "hr_salary_rule_category_acc_threshold",
            "hr_salary_rule_category_ac_open",
            "hr_salary_rule_category_laa_base",
            "hr_salary_rule_category_laa_threshold",
            "hr_salary_rule_category_laa_salary",
            "hr_salary_rule_category_laac_base",
            "hr_salary_rule_category_laac_salary_max_1",
            "hr_salary_rule_category_laac_salary_max_2",
            "hr_salary_rule_category_laac_salary_min_1",
            "hr_salary_rule_category_laac_salary_min_2",
            "hr_salary_rule_category_laac_salary_1",
            "hr_salary_rule_category_laac_salary_2",
            "hr_salary_rule_category_ijm_base",
            "hr_salary_rule_category_ijm_salary_max_1",
            "hr_salary_rule_category_ijm_salary_max_2",
            "hr_salary_rule_category_ijm_salary_min_1",
            "hr_salary_rule_category_ijm_salary_min_2",
            "hr_salary_rule_category_ijm_salary_1",
            "hr_salary_rule_category_ijm_salary_2",
            "hr_salary_rule_category_indemnite_perte_gain",
            "hr_salary_rule_category_is_base",
            "hr_salary_rule_category_is_salary",
            "hr_salary_rule_category_is_dt_aperiodic_salary",
            "hr_salary_rule_category_is_dt_periodic_salary",
            "hr_salary_rule_category_is_dt_salary",
            "hr_salary_rule_category_is_rate",
            "hr_salary_rule_category_as_days",
            "hr_salary_rule_category_ch_days",
            "hr_salary_rule_category_worked_days",
            "hr_salary_rule_category_is_salary_dt_p",
            "hr_salary_rule_category_is_salary_dt_ap",
        ],
        "eg": [
            "hr_salary_rule_category_eg_tax_totals",
            "TOTAL",
            "C_IMP",
            "RETENUES",
            "SALC",
            "PREV",
            "SECU",
            "other_totals",
        ],
        "fr": ["TOTAL", "C_IMP", "RETENUES", "SALC", "PREV", "SECU", "other_totals"],
        "hk": ["AUTOPAY", "MPF", "EEMPF", "ERMPF"],
        "id": [
            "PPH21",
            "PPH21_yearly",
            "PTKP",
            "PKP",
            "BASE",
            "JABATAN",
            "YEARLY_GROSS",
        ],
        "in": ["SPA", "LEAVE", "PBS"],
        "jo": [
            "hr_salary_rule_category_jo_tax_brackets",
            "hr_salary_rule_category_jo_ssd",
        ],
        "ke": [
            "KE_UT_ALW",
            "KE_T_ALW",
            "EXEMPTION",
            "NSSF",
            "RELIEF",
            "STATUTORY_DED",
            "OTHER_DED",
            "INS_RELIEF",
            "INSURANCES",
            "TOTAL_DED",
            "HIDDEN",
        ],
        "lt": ["hr_salary_rule_category_ssc_employer"],
        "lu": [
            "hr_salary_rule_category_vpa",
            "hr_salary_rule_category_supplements_accessories",
            "hr_salary_rule_category_overtime_pay",
            "hr_salary_rule_category_overtime_premiums",
            "hr_salary_rule_category_bonuses_bic_bik",
            "hr_salary_rule_category_unemployment_weather_cyclical",
            "hr_salary_rule_category_contribution",
            "hr_salary_rule_category_taxes",
            "hr_salary_rule_category_tax_credit",
            "hr_salary_rule_category_removed_from_net",
            "hr_salary_rule_category_meal_vouchers",
            "hr_salary_rule_category_total_contributions",
            "hr_salary_rule_category_total_allowances",
            "hr_salary_rule_category_taxable_amount",
            "hr_salary_rule_category_net_to_pay",
            "hr_salary_rule_category_bik",
            "hr_salary_rule_category_gratification",
            "hr_salary_rule_category_net_gratification",
        ],
        "ma": ["SALC", "DEDIRPP", "UNTAXABLE_DED", "INCOME_TAX", "O_TOTAL"],
        "mx": [
            "hr_payroll_integrated_daily_wage",
            "hr_payroll_social_security_employee",
            "hr_payroll_social_security_employer",
            "hr_payroll_social_security_employee_total",
            "hr_payroll_social_security_employer_total",
        ],
        "nl": [
            "hr_salary_rule_category_social_security_employee",
            "hr_salary_rule_category_income_tax",
            "hr_salary_rule_category_social_security_employer",
            "hr_salary_rule_category_taxable_income",
        ],
        "pk": [
            "pk_tax_deduction_salary_rule_category",
            "pk_tax_bracket_salary_rule_category",
        ],
        "pl": [
            "social_security_employee",
            "social_security_employer",
            "social_security_employee_total",
            "social_security_employer_total",
            "standard_earning",
            "taxable_amount",
            "withholding_taxes",
        ],
        "ro": [
            "l10n_ro_cas_category",
            "l10n_ro_cass_category",
            "l10n_ro_income_tax_category",
            "l10n_ro_cam_category",
            "l10n_ro_unemployed_disabled_category",
            "l10n_ro_pension_category",
        ],
        "sk": [
            "hr_payroll_meal_vouchers_employee",
            "hr_payroll_meal_vouchers_employer",
            "hr_payroll_social_security_employee",
            "hr_payroll_social_security_employer",
            "hr_payroll_social_security_employee_total",
            "hr_payroll_social_security_employer_total",
            "hr_payroll_income_tax_employee",
            "hr_payroll_income_tax_employee_total",
        ],
        "tr": [
            "hr_salary_rule_category_tr_ssid",
            "hr_salary_rule_category_tr_taxded",
            "hr_salary_rule_category_tr_net_taxded",
            "hr_salary_rule_category_tr_ssid_net",
            "hr_salary_rule_category_tr_taxbase",
            "hr_salary_rule_category_tr_stamp_tax",
            "hr_salary_rule_category_tax_deduction_net",
        ],
        "us": [
            "hr_payroll_pre_tax_benefits",
            "hr_payroll_benefits_matching",
            "hr_payroll_taxable",
            "hr_payroll_taxes",
            "hr_payroll_post_tax_deductions",
            "hr_payroll_employer_deductions",
        ],
    }

    for country_code, xmlids in xmlids_by_country.items():
        if not util.module_installed(cr, f"l10n_{country_code}_hr_payroll"):
            continue
        country_id = util.ref(cr, f"base.{country_code}")
        for xmlid in xmlids:
            rule_id = util.ref(cr, f"l10n_{country_code}_hr_payroll.{xmlid}")
            cr.execute(
                """
                UPDATE hr_salary_rule_category
                   SET country_id = %s
                 WHERE id = %s
            """,
                [country_id, rule_id],
            )

    if util.module_installed(cr, "l10n_be_hr_payroll_fleet"):
        country_id = util.ref(cr, "base.be")
        rule_id = util.ref(cr, "l10n_be_hr_payroll_fleet.hr_salary_rule_category_co2_fee")
        cr.execute(
            """
            UPDATE hr_salary_rule_category
               SET country_id = %s
             WHERE id = %s
        """,
            [country_id, rule_id],
        )

    if util.module_installed(cr, "l10n_ma_hr_payroll"):
        util.remove_record(cr, "l10n_ma_hr_payroll.COMP")

    for field in ["department_id", "job_id", "structure_type_id"]:
        util.remove_field(cr, "hr.payslip.employees", field)

    util.remove_field(cr, "hr.payslip", "number")
