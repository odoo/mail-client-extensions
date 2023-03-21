from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_mx_edi_stock_extended.l10n_mx_edi_cartaporte_report_hazardous")
