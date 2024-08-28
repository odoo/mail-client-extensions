from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "stock.picking", "l10n_mx_edi_customs_no")
    util.remove_view(cr, "l10n_mx_edi_stock_extended.product_template_form_inherit_l10n_mx_edi_stock_extended_30")
    util.remove_view(cr, "l10n_mx_edi_stock_extended.stock_picking_form_inherit_l10n_mx_edi_stock_extended_30")
