from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "stock.picking", "l10n_mx_edi_origin", "l10n_mx_edi_cfdi_origin")
    util.rename_field(cr, "stock.picking", "l10n_mx_edi_cancel_picking_id", "l10n_mx_edi_cfdi_cancel_picking_id")
    util.rename_field(cr, "stock.picking", "l10n_mx_edi_cfdi_file_id", "l10n_mx_edi_cfdi_attachment_id")

    util.change_field_selection_values(
        cr,
        "stock.picking",
        "l10n_mx_edi_status",
        {
            "cancelled": "cancel",
        },
    )
    query = """
        UPDATE stock_picking
        SET l10n_mx_edi_status = NULL
        WHERE l10n_mx_edi_status NOT IN ('sent', 'cancel')
        AND l10n_mx_edi_status IS NOT NULL
    """
    util.explode_execute(cr, query, table="stock_picking")
    util.rename_field(cr, "stock.picking", "l10n_mx_edi_status", "l10n_mx_edi_cfdi_state")
    util.rename_field(cr, "stock.picking", "l10n_mx_edi_is_export", "l10n_mx_edi_external_trade")
    util.change_field_selection_values(
        cr,
        "stock.picking",
        "l10n_mx_edi_sat_status",
        {
            "none": "not_defined",
        },
    )
    util.rename_field(cr, "stock.picking", "l10n_mx_edi_sat_status", "l10n_mx_edi_cfdi_sat_state")

    util.create_column(cr, 'stock_picking', 'l10n_mx_edi_is_cfdi_needed', 'bool')

    query = """
        UPDATE stock_picking
        SET l10n_mx_edi_is_cfdi_needed = True
        FROM res_company
        JOIN res_country ON res_country.id = res_company.account_fiscal_country_id
        WHERE res_company.id = stock_picking.company_id AND res_country.code = 'MX'
    """
    util.explode_execute(cr, query, table="stock_picking")

    util.remove_field(cr, "stock.picking", "l10n_mx_edi_content")
    util.remove_field(cr, "stock.picking", "l10n_mx_edi_error")

    util.rename_xmlid(
        cr, "l10n_mx_edi_stock.view_picking_edi_form", "l10n_mx_edi_stock.stock_picking_form_inherit_l10n_mx_edi_stock"
    )

