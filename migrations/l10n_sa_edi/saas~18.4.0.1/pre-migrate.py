from odoo.upgrade import util


def migrate(cr, version):
    # Remove UBL templates
    util.remove_view(cr, "l10n_sa_edi.ubl_21_DebitNoteType_zatca")
    util.remove_view(cr, "l10n_sa_edi.ubl_21_CreditNoteType_zatca")
    util.remove_view(cr, "l10n_sa_edi.ubl_21_InvoiceType_zatca")
    util.remove_view(cr, "l10n_sa_edi.ubl_21_AddressType_zatca")
    util.remove_view(cr, "l10n_sa_edi.ubl_21_PartyType_zatca")
    util.remove_view(cr, "l10n_sa_edi.ubl_21_TaxTotalType_zatca")
    util.remove_view(cr, "l10n_sa_edi.ubl_21_DebitNoteLineType_zatca")
    util.remove_view(cr, "l10n_sa_edi.ubl_21_CreditNoteLineType_zatca")
    util.remove_view(cr, "l10n_sa_edi.ubl_21_InvoiceLineType_zatca")
    util.remove_view(cr, "l10n_sa_edi.ubl_21_PaymentMeansType_zatca")
