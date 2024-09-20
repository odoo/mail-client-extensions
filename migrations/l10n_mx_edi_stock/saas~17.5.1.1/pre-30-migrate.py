from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_mx_edi_stock.stock_picking_form_inherit_l10n_mx_edi_stock_extended")
    util.remove_view(cr, "l10n_mx_edi_stock.l10n_mx_edi_cartaporte_report_hazard_has_serial_move_line")
    util.remove_view(cr, "l10n_mx_edi_stock.l10n_mx_edi_cartaporte_report_hazard_aggregated_move_lines")
    util.remove_view(cr, "l10n_mx_edi_stock.l10n_mx_edi_cartaporte_report_delivery_comex")
    util.remove_view(cr, "l10n_mx_edi_stock.cfdi_cartaporte_comex")
