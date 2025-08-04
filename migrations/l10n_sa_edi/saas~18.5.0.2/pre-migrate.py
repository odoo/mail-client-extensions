from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.journal", "l10n_sa_serial_number")
    util.remove_view(cr, "l10n_sa_edi.arabic_english_invoice")
