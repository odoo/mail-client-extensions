from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    if fund := env.ref("l10n_au_hr_payroll.hr_payroll_super_fund", raise_if_not_found=False):
        fund.usi = "usi123123123123"
