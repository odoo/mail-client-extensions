from odoo.upgrade import util


def migrate(cr, version):
    # Remove UBL templates
    util.remove_view(cr, "l10n_my_edi.ubl_20_InvoiceLineType_my")
    util.remove_view(cr, "l10n_my_edi.ubl_20_DeliveryType_my")
    util.remove_view(cr, "l10n_my_edi.ubl_21_InvoiceType_my")
