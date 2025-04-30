from odoo.upgrade import util


def migrate(cr, version):
    if util.modules_installed(cr, "account_budget"):
        util.force_install_module(cr, "account_budget_purchase")
