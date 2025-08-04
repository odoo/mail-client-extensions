from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_gcc_invoice.arabic_english_invoice")
