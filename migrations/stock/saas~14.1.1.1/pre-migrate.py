# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, xml_id="stock.view_picking_type_list")

    util.remove_field(cr, "stock.picking.type", "rate_picking_late")
    util.remove_field(cr, "stock.picking.type", "rate_picking_backorders")
    util.remove_field(cr, "stock.warehouse", "warehouse_count")
    util.remove_field(cr, "stock.warehouse", "show_resupply")
