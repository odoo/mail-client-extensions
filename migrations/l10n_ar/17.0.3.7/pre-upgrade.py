from odoo.upgrade import util


def migrate(cr, version):
    util.alter_column_type(cr, "account_move", "l10n_ar_currency_rate", "float8")
