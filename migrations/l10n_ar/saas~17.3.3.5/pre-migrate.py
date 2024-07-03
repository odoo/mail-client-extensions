from odoo.upgrade import util


def migrate(cr, version):
    # A new computed stored field invoice_currency_rate was added to model 'account.move'.
    # This makes the l10n_ar_currency_rate field from this module obsolete
    util.remove_field(cr, "account.move", "l10n_ar_currency_rate")

    util.remove_field(cr, "res.partner", "l10n_ar_special_purchase_document_type_ids")
