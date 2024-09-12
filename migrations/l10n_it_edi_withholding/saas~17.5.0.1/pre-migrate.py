from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_it_edi_withholding.account_invoice_line_it_FatturaPA_withholding")
