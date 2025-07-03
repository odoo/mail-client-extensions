from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, "l10n_au_hr_payroll_account.hr_department_rdau", "l10n_au_hr_payroll.au_hr_department_rd")
    util.rename_xmlid(
        cr, "l10n_au_hr_payroll_account.job_developer_australian", "l10n_au_hr_payroll.au_hr_job_developer"
    )
    util.rename_xmlid(cr, *eb("l10n_au_hr_payroll.hr_employee_{au,roger}"))
    util.rename_xmlid(cr, *eb("l10n_au_hr_payroll.hr_contract_{au,roger}"))
    util.rename_xmlid(cr, *eb("l10n_au_hr_payroll{_account,}.res_partner_dennis"))
    util.rename_xmlid(cr, *eb("l10n_au_hr_payroll{_account,}.user_dennis"))
    util.rename_xmlid(cr, *eb("l10n_au_hr_payroll{_account,}.res_partner_dennis_work_address"))
    util.rename_xmlid(cr, *eb("l10n_au_hr_payroll{_account,}.res_partner_dennis_private_address"))
    util.rename_xmlid(cr, *eb("l10n_au_hr_payroll{_account,}.res_partner_bank_account_dennis"))
    util.rename_xmlid(cr, *eb("l10n_au_hr_payroll{_account,}.hr_employee_dennis"))
    util.rename_xmlid(cr, *eb("l10n_au_hr_payroll{_account,}.hr_contract_cdi_dennis_previous"))
    util.rename_xmlid(cr, *eb("l10n_au_hr_payroll{_account,}.hr_contract_cdi_dennis"))

    util.remove_record(cr, "l10n_au_hr_payroll.l10n_au_payslip_employee_bank_account")
    util.remove_record(cr, "l10n_au_hr_payroll.res_partner_employee_au")

    util.remove_view(cr, "l10n_au_hr_payroll.view_employee_form")
    util.rename_field(cr, "l10n_au.termination.payment", "contract_id", "version_id")

    columns = [
        "l10n_au_tfn_declaration",
        "l10n_au_tfn",
        "l10n_au_nat_3093_amount",
        "l10n_au_extra_pay",
        "l10n_au_training_loan",
        "l10n_au_medicare_exemption",
        "l10n_au_medicare_surcharge",
        "l10n_au_medicare_reduction",
        "l10n_au_tax_free_threshold",
        "l10n_au_child_support_deduction",
        "l10n_au_child_support_garnishee_amount",
        "l10n_au_employment_basis_code",
        "l10n_au_tax_treatment_category",
        "l10n_au_income_stream_type",
        "l10n_au_tax_treatment_option_actor",
        "l10n_au_less_than_3_performance",
        "l10n_au_tax_treatment_option_voluntary",
        "l10n_au_tax_treatment_option_seniors",
        "l10n_au_comissioners_installment_rate",
        "l10n_au_tax_treatment_code",
        "l10n_au_work_country_id",
        "l10n_au_withholding_variation",
        "l10n_au_withholding_variation_amount",
        "l10n_au_additional_withholding_amount",
    ]
    move_columns = util.import_script("hr/saas~18.4.1.1/post-migrate.py").move_columns
    move_columns(cr, columns)
