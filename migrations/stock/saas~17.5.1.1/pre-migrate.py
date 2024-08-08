from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "stock.location", "sequence")
    util.remove_field(cr, "stock.picking", "hide_picking_type")
