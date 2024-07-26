from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("""
    UPDATE hr_employee
       SET disabled = l10n_ke_disabled
     WHERE l10n_ke_disabled is true
    """)
    util.remove_field(cr, "hr.employee", "l10n_ke_disabled")
    util.remove_view(cr, "l10n_ke_hr_payroll.hr_employee_view_form")
