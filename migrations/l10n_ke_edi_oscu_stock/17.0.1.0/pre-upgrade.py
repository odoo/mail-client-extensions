from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "stock_move", "l10n_ke_oscu_flow_type_code", "varchar")
