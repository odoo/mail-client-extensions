from odoo.upgrade import util


def migrate(cr, version):
    util.recompute_fields(cr, "stock.move", ["l10n_ke_oscu_flow_type_code"])
