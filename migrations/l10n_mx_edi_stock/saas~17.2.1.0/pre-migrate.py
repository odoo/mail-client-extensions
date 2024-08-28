from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_mx_edi_stock.cfdi_cartaporte_30")
    util.remove_view(cr, "l10n_mx_edi_stock.l10n_mx_edi_vehicle_form_inherit_l10n_mx_edi_stock_30")
    util.remove_view(cr, "l10n_mx_edi_stock.stock_picking_form_inherit_l10n_mx_edi_stock_30")
    util.create_column(cr, "l10n_mx_edi_vehicle", "gross_vehicle_weight", "float8")
    util.create_column(cr, "stock_picking", "l10n_mx_edi_gross_vehicle_weight", "float8")
