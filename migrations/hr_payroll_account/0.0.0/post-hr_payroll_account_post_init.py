from odoo.addons.hr_payroll_account import _hr_payroll_account_post_init

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_gte("17.0"):
        # if some SLR journal exists the hook in hr_payroll may fail
        # we do not want to run the pre_init hook to avoid renaming SLR journals
        cr.execute("SELECT 1 FROM account_journal WHERE code = 'SLR'")
        if not cr.rowcount:
            _hr_payroll_account_post_init(util.env(cr))
