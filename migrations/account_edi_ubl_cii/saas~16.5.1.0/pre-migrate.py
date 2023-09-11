from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_edi_ubl_cii.ubl_21_InvoiceLineType")
