from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(
        cr,
        "res.partner.bank",
        "l10n_us_bank_account_type",
        "l10n_us_payment_nacha",
        "l10n_us",
    )
