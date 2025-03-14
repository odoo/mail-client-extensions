from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "stock_picking", "l10n_mx_edi_gross_vehicle_weight", "float8")
