from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_pe_edi.pe_ubl_2_1_void_documents")
    util.remove_view(cr, "l10n_pe_edi.pe_ubl_2_1_debit_note")
    util.remove_view(cr, "l10n_pe_edi.pe_ubl_2_1_debit_note_body")
    util.remove_view(cr, "l10n_pe_edi.pe_ubl_2_1_debit_note_line")
    util.remove_view(cr, "l10n_pe_edi.pe_ubl_2_1_credit_note")
    util.remove_view(cr, "l10n_pe_edi.pe_ubl_2_1_refund_body")
    util.remove_view(cr, "l10n_pe_edi.pe_ubl_2_1_refund_line")
    util.remove_view(cr, "l10n_pe_edi.pe_ubl_2_1_invoice")
    util.remove_view(cr, "l10n_pe_edi.pe_ubl_2_1_invoice_body")
    util.remove_view(cr, "l10n_pe_edi.pe_ubl_2_1_invoice_line")
    util.remove_view(cr, "l10n_pe_edi.pe_ubl_2_1_signature")
    util.remove_view(cr, "l10n_pe_edi.pe_ubl_2_1_common")
    util.remove_view(cr, "l10n_pe_edi.pe_ubl_2_1_common_line")
