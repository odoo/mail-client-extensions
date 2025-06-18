from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_move", "l10n_jo_edi_invoice_type", "varchar")

    # Remove UBL templates
    util.remove_view(cr, "l10n_jo_edi.ubl_jo_TaxTotalType")
    util.remove_view(cr, "l10n_jo_edi.ubl_jo_InvoiceLineType")
    util.remove_view(cr, "l10n_jo_edi.ubl_jo_PaymentMeansType")
    util.remove_view(cr, "l10n_jo_edi.ubl_jo_Invoice")
    util.remove_view(cr, "l10n_jo_edi.ubl_jo_InvoiceType")
