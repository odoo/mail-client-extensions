from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_move", "l10n_dk_currency_rate_at_transaction", "numeric")
