from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_move", "l10n_jo_edi_invoice_type", "varchar")
