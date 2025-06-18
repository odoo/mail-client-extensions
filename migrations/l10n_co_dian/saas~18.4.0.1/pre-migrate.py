from odoo.upgrade import util


def migrate(cr, version):
    # Remove UBL templates
    util.remove_view(cr, "l10n_co_dian.ubl_20_Invoice_dian")
    util.remove_view(cr, "l10n_co_dian.ubl_20_CreditNote_dian")
    util.remove_view(cr, "l10n_co_dian.ubl_20_DebitNote_dian")
