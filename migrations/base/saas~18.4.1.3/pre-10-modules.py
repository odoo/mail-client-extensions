from odoo.upgrade import util


def migrate(cr, version):
    util.rename_module(cr, "hr_contract_sign", "hr_sign")
    util.rename_module(cr, "base_automation_hr_contract", "base_automation_hr")
    util.rename_module(cr, "hr_work_entry_contract_attendance", "hr_work_entry_attendance")
    util.rename_module(cr, "hr_work_entry_contract_enterprise", "hr_work_entry_enterprise")
    util.rename_module(cr, "hr_work_entry_contract_planning", "hr_work_entry_planning")
    util.rename_module(cr, "hr_work_entry_contract_planning_attendance", "hr_work_entry_planning_attendance")

    util.merge_module(cr, "hr_contract", "hr")
    util.merge_module(cr, "hr_holidays_contract_gantt", "hr_holidays_gantt")
    util.merge_module(cr, "esg_hr_contract", "esg_hr")
    util.merge_module(cr, "hr_holidays_contract", "hr_holidays")
    util.merge_module(cr, "project_enterprise_hr_contract", "project_enterprise_hr")
    util.merge_module(cr, "hr_work_entry_contract", "hr_work_entry")
    util.merge_module(cr, "planning_contract", "planning")
    util.merge_module(cr, "documents_hr_contract", "documents_hr")
    util.merge_module(cr, "hr_appraisal_contract", "hr_appraisal")
    util.merge_module(cr, "l10n_ch_hr_payroll_elm_transmission", "l10n_ch_hr_payroll")
    util.merge_module(cr, "l10n_ch_hr_payroll_elm_transmission_account", "l10n_ch_hr_payroll_account")
    util.merge_module(cr, "l10n_jo_edi_extended", "l10n_jo_edi")
    util.merge_module(cr, "l10n_ae_corporate_tax_report", "l10n_ae_reports")

    util.remove_module(cr, "test_hr_contract_calendar")
    util.remove_module(cr, "spreadsheet_dashboard_hr_contract")
    util.remove_module(cr, "hr_contract_reports")
