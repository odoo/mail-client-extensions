from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_ch_hr_payroll_account.swissdec_wage_types_tree")
    util.remove_view(cr, "l10n_ch_hr_payroll_account.hr_salary_rule_view_tree_l10n_ch_wage_types")
