from odoo.upgrade import util


def migrate(cr, version):
    util.change_field_selection_values(
        cr,
        "res.partner",
        "peppol_eas",
        {"0037": "0216", "0215": "0216"},
    )
    util.remove_view(cr, "account_edi_ubl_cii.res_partner_view_tree")
    util.remove_view(cr, "account_edi_ubl_cii.res_partner_view_search")
    util.remove_view(cr, "account_edi_ubl_cii.res_config_settings_view_form")
    util.remove_field(cr, "res.company", "invoice_is_ubl_cii")
    util.remove_field(cr, "res.config.settings", "invoice_is_ubl_cii")
