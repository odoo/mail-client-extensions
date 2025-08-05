from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    if fund := env.ref("l10n_au_hr_payroll_account.super_fund_example_super", raise_if_not_found=False):
        fund.usi = "1309011309"
