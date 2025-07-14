from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_hk_hr_payroll.hr_payslip_run_form_inherit_l10n_hk_hr_payroll")
