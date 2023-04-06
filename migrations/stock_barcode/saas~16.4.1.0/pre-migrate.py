from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "stock.move.line", "picking_location_id")
    util.remove_field(cr, "stock.move.line", "picking_location_dest_id")
