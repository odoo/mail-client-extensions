from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("l10n_us_hr_payroll.{hr_department_rdus,us_hr_department_rd}"))
    util.rename_xmlid(cr, *eb("l10n_us_hr_payroll.{job_developer_united_states,us_hr_job_developer}"))
    util.rename_xmlid(cr, *eb("l10n_us_hr_payroll.hr_contract_{cdi_,}maggie_previous"))
    util.rename_xmlid(cr, *eb("l10n_us_hr_payroll.hr_contract_{cdi_,}maggie"))

    util.remove_record(cr, "l10n_us_hr_payroll.res_partner_maggie_work_contact")
    util.remove_record(cr, "l10n_us_hr_payroll.res_partner_bank_account_norberta")

    util.update_record_from_xml(
        cr, "l10n_us_hr_payroll.hr_payroll_dashboard_warning_employee_wa_without_worker_compensation"
    )

    columns = [
        "l10n_us_old_w4",
        "l10n_us_w4_step_2",
        "l10n_us_w4_step_3",
        "l10n_us_w4_step_4a",
        "l10n_us_w4_step_4b",
        "l10n_us_w4_step_4c",
        "l10n_us_w4_allowances_count",
        "l10n_us_w4_withholding_deduction_allowances",
        "l10n_us_filing_status",
        "l10n_us_state_filing_status",
        "l10n_us_statutory_employee",
        "l10n_us_retirement_plan",
        "l10n_us_third_party_sick_pay",
        "l10n_us_state_withholding_allowance",
        "l10n_us_state_extra_withholding",
    ]

    move_columns = util.import_script("l10n_au_hr_payroll/saas~18.4.1.0/pre-migrate.py").move_columns
    move_columns(cr, employee_columns=columns)

    util.make_field_non_stored(cr, "hr.employee", "l10n_us_old_w4")
    util.make_field_non_stored(cr, "hr.employee", "l10n_us_w4_step_2")
    util.make_field_non_stored(cr, "hr.employee", "l10n_us_w4_step_3")
    util.make_field_non_stored(cr, "hr.employee", "l10n_us_w4_step_4a")
    util.make_field_non_stored(cr, "hr.employee", "l10n_us_w4_step_4b")
    util.make_field_non_stored(cr, "hr.employee", "l10n_us_w4_step_4c")
    util.make_field_non_stored(cr, "hr.employee", "l10n_us_w4_allowances_count")
    util.make_field_non_stored(cr, "hr.employee", "l10n_us_w4_withholding_deduction_allowances")
    util.make_field_non_stored(cr, "hr.employee", "l10n_us_filing_status")
    util.make_field_non_stored(cr, "hr.employee", "l10n_us_state_filing_status")
    util.make_field_non_stored(cr, "hr.employee", "l10n_us_statutory_employee")
    util.make_field_non_stored(cr, "hr.employee", "l10n_us_retirement_plan")
    util.make_field_non_stored(cr, "hr.employee", "l10n_us_third_party_sick_pay")
    util.make_field_non_stored(cr, "hr.employee", "l10n_us_state_withholding_allowance")
    util.make_field_non_stored(cr, "hr.employee", "l10n_us_state_extra_withholding")

    util.remove_view(cr, "l10n_us_hr_payroll.hr_contract_view_form")
