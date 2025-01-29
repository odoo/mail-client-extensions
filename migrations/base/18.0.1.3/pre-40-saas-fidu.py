import os

from odoo.upgrade import util


def migrate(cr, version):
    # Automatically install base_automation for saas fiduciaries which have documents and account_accountant. This variable comes from SaaS.
    need_automation = util.str2bool(os.getenv("ODOO_UPG_SAAS_ONEAPPFREE", "0"))
    if need_automation and util.modules_installed(cr, "documents", "account_accountant", "saas_trial"):
        util.install_module(cr, "base_automation")
