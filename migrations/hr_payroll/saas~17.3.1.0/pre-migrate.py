from odoo.upgrade import util


def migrate(cr, version):
    module_name = "hr_payroll_account_iso20022" if util.version_gte("saas~17.5") else "hr_payroll_account_sepa"
    if util.module_installed(cr, module_name):
        fields = (
            ("sepa_export", "payment_report"),
            ("sepa_export_filename", "payment_report_filename"),
            ("sepa_export_date", "payment_report_date"),
        )
        for model in ("hr.payslip", "hr.payslip.run"):
            for old_field, new_field in fields:
                util.move_field_to_module(cr, model, old_field, module_name, "hr_payroll")
                util.rename_field(cr, model, old_field, new_field)
