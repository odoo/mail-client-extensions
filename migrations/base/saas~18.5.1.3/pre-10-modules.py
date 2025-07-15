from odoo.upgrade import util


def migrate(cr, version):
    if util.modules_installed(cr, "account_budget"):
        util.force_install_module(cr, "account_budget_purchase")
    util.merge_module(cr, "l10n_be_reports_prorata", "l10n_be_reports")
