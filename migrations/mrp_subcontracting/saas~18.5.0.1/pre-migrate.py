from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "stock.picking", "display_action_record_components")
