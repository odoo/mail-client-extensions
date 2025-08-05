from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.remove_view(cr, "l10n_in_ewaybill.l10n_in_einvoice_report_invoice_document_inherit")
    util.remove_view(cr, "l10n_in_ewaybill.invoice_form_inherit_l10n_in_edi_ewaybill")
    util.rename_field(cr, "res.company", *eb("l10n_in{_edi,}_ewaybill_username"))
    util.rename_field(cr, "res.company", *eb("l10n_in{_edi,}_ewaybill_password"))
    util.rename_field(cr, "res.company", *eb("l10n_in{_edi,}_ewaybill_auth_validity"))
    util.rename_field(cr, "res.config.settings", *eb("l10n_in{_edi,}_ewaybill_username"))
    util.rename_field(cr, "res.config.settings", *eb("l10n_in{_edi,}_ewaybill_password"))
    if util.module_installed(cr, "l10n_in_ewaybill_stock"):
        models = util.splitlines(
            """
            l10n.in.ewaybill
            l10n.in.ewaybill.cancel
            """
        )
        for m in models:
            util.move_model(cr, m, *eb("l10n_in_ewaybill{_stock,}"))
        fields = util.splitlines(
            """
            type_description
            picking_id
            move_ids
            fiscal_position_id
            """
        )
        for f in fields:
            util.move_field_to_module(cr, "l10n.in.ewaybill", f, *eb("l10n_in_ewaybill{,_stock}"))
        util.rename_xmlid(cr, *eb("l10n_in_ewaybill{_stock,}.view_ewaybill_cancel_form"))
        util.rename_xmlid(cr, *eb("l10n_in_ewaybill{_stock,}.paperformat_ewaybill"))
        util.rename_xmlid(cr, *eb("l10n_in_ewaybill{_stock,}.report_ewaybill"))
        util.rename_xmlid(cr, *eb("l10n_in_ewaybill{_stock,}.action_report_ewaybill"))

    util.remove_view(cr, "l10n_in_ewaybill.invoice_form_inherit_l10n_in_ewaybill_port")
    # This avoids errors if the `l10n_in_ewaybill_port` module is not already installed.
    util.create_column(cr, "account_move", "l10n_in_ewaybill_port_partner_id", "int4")
