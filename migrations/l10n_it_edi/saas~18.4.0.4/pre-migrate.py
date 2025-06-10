from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_it_edi.account_invoice_it_FatturaPA_export_debit_note")
