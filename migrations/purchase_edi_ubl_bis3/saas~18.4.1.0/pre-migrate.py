from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "purchase_edi_ubl_bis3.portal_connect_software_modal")

    util.remove_view(cr, "purchase_edi_ubl_bis3.bis3_OrderType")
    util.remove_view(cr, "purchase_edi_ubl_bis3.bis3_LineItemType")
    util.remove_view(cr, "purchase_edi_ubl_bis3.bis3_ItemType")
    util.remove_view(cr, "purchase_edi_ubl_bis3.bis3_AnticipatedMonetaryTotalType")
    util.remove_view(cr, "purchase_edi_ubl_bis3.bis3_DeliveryType")
    util.remove_view(cr, "purchase_edi_ubl_bis3.bis3_AllowanceChargeType")
    util.remove_view(cr, "purchase_edi_ubl_bis3.bis3_TaxCategoryType")
    util.remove_view(cr, "purchase_edi_ubl_bis3.bis3_PaymentTermsType")
    util.remove_view(cr, "purchase_edi_ubl_bis3.bis3_PartyType")
    util.remove_view(cr, "purchase_edi_ubl_bis3.bis3_ContactType")
    util.remove_view(cr, "purchase_edi_ubl_bis3.bis3_AddressType")
