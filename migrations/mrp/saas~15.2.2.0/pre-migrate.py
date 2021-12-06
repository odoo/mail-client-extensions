# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "mrp.access_stock_location_mrp_worker")
    util.remove_record(cr, "mrp.access_stock_move_mrp_worker")
    util.remove_record(cr, "mrp.access_stock_picking_mrp_worker")
    util.remove_record(cr, "mrp.access_stock_warehouse")
    util.remove_record(cr, "mrp.access_stock_move_mrp_manager")
    util.remove_record(cr, "mrp.access_stock_production_lot_user")
    util.remove_record(cr, "mrp.access_stock_warehouse_orderpoint_user")
    util.remove_record(cr, "mrp.access_stock_picking_mrp_manager")
