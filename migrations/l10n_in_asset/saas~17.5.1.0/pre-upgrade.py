from odoo.upgrade import util


def migrate(cr, version):
    util.update_field_usage(cr, "account.asset", "l10n_in_fiscal_code", "country_code")
    util.remove_field(cr, "account.asset", "l10n_in_fiscal_code")
