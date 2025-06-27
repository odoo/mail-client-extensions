from odoo.upgrade import util


def migrate(cr, version):
    util.recompute_fields(cr, "account.move", ["l10n_dk_currency_rate_at_transaction"])
