from odoo.upgrade import util


def migrate(cr, version):
    if util.has_enterprise():
        util.rename_module(cr, "pos_l10n_se", "l10n_se_pos")
        util.merge_module(cr, "l10n_ke_hr_payroll_shif", "l10n_ke_hr_payroll")
