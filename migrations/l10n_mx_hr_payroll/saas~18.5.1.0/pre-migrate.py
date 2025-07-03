from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.version", "l10n_mx_schedule_pay")
    util.remove_field(cr, "hr.payroll.structure.type", "l10n_mx_default_schedule_pay")
    util.remove_field(cr, "hr.payroll.structure", "l10n_mx_default_schedule_pay")
    util.remove_field(cr, "hr.payroll.structure", "l10n_mx_schedule_pay")
    util.remove_field(cr, "hr.payroll.structure", "country_code")
    util.remove_view(cr, "l10n_mx_hr_payroll.hr_payroll_structure_type_view_form")
    util.remove_view(cr, "l10n_mx_hr_payroll.hr_payroll_structure_view_form")
