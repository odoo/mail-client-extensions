from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "hr_payroll.access_hr_payslip_run_employee_manager")
    util.remove_record(cr, "hr_payroll.hr_payroll_dashboard_warning_employee_with_different_company_on_contract")
    util.remove_record(cr, "hr_payroll.hr_payroll_dashboard_warning_employee_ambiguous_contract")
    util.remove_record(cr, "hr_payroll.hr_payroll_dashboard_warning_new_contracts")
    util.remove_record(cr, "hr_payroll.menu_hr_payroll_employees_root")
    util.remove_record(cr, "hr_payroll.hr_menu_all_contracts")

    util.rename_field(cr, "hr.payroll.headcount.line", "contract_names", "version_names")
    util.rename_field(cr, "hr.payroll.headcount.line", "contract_id", "version_id")
    util.rename_field(cr, "hr.payslip", "contract_id", "version_id")
    util.rename_field(cr, "hr.payslip.line", "contract_id", "version_id")
    util.rename_field(cr, "hr.payslip.worked_days", "contract_id", "version_id")
    util.rename_field(cr, "hr.payslip.input", "contract_id", "version_id")
    util.rename_field(cr, "hr.payroll.edit.payslip.line", "contract_id", "version_id")
    util.rename_field(cr, "hr.work.entry.export.employee.mixin", "contract_ids", "version_ids")
    util.rename_field(cr, "hr.payroll.index", "contract_ids", "version_ids")

    util.remove_field(cr, "hr.payslip", "contract_domain_ids")
    util.remove_field(cr, "hr.version", "salary_attachments_count")
    util.remove_field(cr, "hr.version", "employee_reference")

    util.remove_view(cr, "hr_payroll.hr_contract_view_tree")
    util.remove_view(cr, "hr_payroll.hr_contract_view_kanban")
    util.remove_view(cr, "hr_payroll.hr_contract_search_inherit")
    util.remove_view(cr, "hr_payroll.hr_contract_form_inherit")

    columns = [
        "is_non_resident",
        "disabled",
    ]
    move_columns = util.import_script("l10n_au_hr_payroll/saas~18.4.1.0/pre-migrate.py").move_columns
    move_columns(cr, employee_columns=columns)
