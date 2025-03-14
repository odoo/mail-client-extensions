from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_edi_ubl_cii.account_invoice_line_facturx_export")
    util.remove_view(cr, "account_edi_ubl_cii.account_invoice_partner_facturx_export")
    util.remove_view(cr, "account_edi_ubl_cii.account_invoice_facturx_export")

    util.remove_view(cr, "account_edi_ubl_cii.export_ubl_invoice_partner")
    util.remove_view(cr, "account_edi_ubl_cii.export_ubl_invoice_line")
    util.remove_view(cr, "account_edi_ubl_cii.export_ubl_invoice")

    util.remove_view(cr, "account_edi_ubl_cii.export_bis3_invoice_partner")
    util.remove_view(cr, "account_edi_ubl_cii.export_bis3_invoice_line")
    util.remove_view(cr, "account_edi_ubl_cii.export_bis3_invoice")
