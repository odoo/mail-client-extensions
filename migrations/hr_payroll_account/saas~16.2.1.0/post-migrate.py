from odoo.addons.hr_payroll_account import _hr_payroll_account_post_init

from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    _hr_payroll_account_post_init(env)
