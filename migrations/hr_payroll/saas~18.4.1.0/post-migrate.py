from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "hr_payroll.hr_payroll_dashboard_warning_employee_missing_from_open_batch")
    util.remove_record(cr, "hr_payroll.hr_payroll_dashboard_warning_working_schedule_change")
    util.update_record_from_xml(cr, "hr_payroll.hr_payroll_dashboard_warning_nearly_expired_contracts")
    util.update_record_from_xml(cr, "hr_payroll.hr_payroll_dashboard_warning_payslips_previous_contract")
    util.update_record_from_xml(cr, "hr_payroll.hr_payroll_dashboard_warning_employee_without_bank_account")
    util.update_record_from_xml(cr, "hr_payroll.hr_payroll_dashboard_warning_employee_without_contract")
    util.update_record_from_xml(cr, "hr_payroll.default_structure")

    util.update_record_from_xml(cr, "hr_payroll.group_hr_payroll_user")
    util.update_record_from_xml(cr, "hr_payroll.group_hr_payroll_manager")

    util.make_field_non_stored(cr, "hr.employee", "is_non_resident")
    util.make_field_non_stored(cr, "hr.employee", "disabled")
