from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "stock.location", "sequence")
    util.remove_field(cr, "stock.picking", "hide_picking_type")
    util.remove_field(cr, "res.config.settings", "group_stock_picking_wave")
    util.remove_record(cr, "stock.group_stock_picking_wave")
    util.remove_model(cr, "stock.scheduler.compute")
    util.remove_record(cr, "stock.menu_procurement_compute")
    util.remove_field(cr, "stock.return.picking", "original_location_id")
    util.remove_field(cr, "stock.return.picking", "parent_location_id")
    util.remove_field(cr, "stock.return.picking", "location_id")
    util.remove_field(cr, "stock.return.picking", "move_dest_exists")
    util.remove_field(cr, "stock.picking.type", "default_location_return_id")
    util.remove_field(cr, "stock.location", "return_location")
