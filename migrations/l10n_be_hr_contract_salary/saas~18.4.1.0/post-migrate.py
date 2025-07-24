from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(
        cr,
        "l10n_be_hr_contract_salary.hr_payroll_dashboard_warning_ip_eligible_contract",
        fields=["evaluation_code"],
    )
    util.update_record_from_xml(
        cr,
        "l10n_be_hr_contract_salary.hr_payroll_dashboard_warning_employee_without_exemption",
        fields=["evaluation_code"],
    )
