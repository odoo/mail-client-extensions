from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "l10n_us_hr_payroll_state_calculation", "l10n_us_hr_payroll")
