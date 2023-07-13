from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr,
        "l10n_mx_edi_stock_extended.view_picking_edi_form_comex",
        "l10n_mx_edi_stock_extended.stock_picking_form_inherit_l10n_mx_edi_stock_extended",
    )
