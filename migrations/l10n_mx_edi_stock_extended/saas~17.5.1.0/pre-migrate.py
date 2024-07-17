from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "stock.picking", "l10n_mx_edi_customs_regime_id")
    util.remove_view(cr, "l10n_mx_edi_stock_extended.stock_picking_form_inherit_l10n_mx_edi_stock_extended_31")
    util.remove_view(cr, "l10n_mx_edi_stock_extended.cfdi_cartaporte_comex_31")
