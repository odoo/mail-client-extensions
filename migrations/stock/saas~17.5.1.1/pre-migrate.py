from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "stock.location", "sequence")
    util.remove_field(cr, "stock.picking", "hide_picking_type")
    util.remove_field(cr, "res.config.settings", "group_stock_picking_wave")
    util.remove_record(cr, "stock.group_stock_picking_wave")
