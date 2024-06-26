from odoo.upgrade import util


def migrate(cr, version):
    # Already moved to l10n_ch_hr_payroll in base script
    util.move_field_to_module(cr, "hr.salary.attachment", "is_quantity", "l10n_ch_hr_payroll", "hr_payroll")
    util.move_field_to_module(cr, "hr.salary.attachment", "is_refund", "l10n_ch_hr_payroll", "hr_payroll")
    util.move_field_to_module(cr, "hr.salary.attachment.type", "is_quantity", "l10n_ch_hr_payroll", "hr_payroll")

    util.create_column(cr, "hr_salary_attachment", "is_refund", "boolean", default=False)
    util.create_column(cr, "hr_salary_attachment_type", "is_quantity", "boolean", default=False)
