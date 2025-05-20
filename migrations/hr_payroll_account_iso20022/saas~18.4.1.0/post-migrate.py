from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(
        cr, "hr_payroll_account_iso20022.hr_payroll_dashboard_warning_employee_invalid_bank_account"
    )
