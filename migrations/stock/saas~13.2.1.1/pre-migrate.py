# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "stock_inventory", "exhausted", "boolean")
    cr.execute("UPDATE stock_inventory SET exhausted = false")

    util.create_column(cr, "stock_move", "delay_alert_date", "timestamp")
    util.create_column(cr, "stock_move", "orderpoint_id", "integer")
    util.remove_field(cr, "stock.move", "string_availability_info")

    util.remove_field(cr, "stock.warehouse.orderpoint", "lead_days")
    util.remove_field(cr, "stock.warehouse.orderpoint", "lead_type")

    util.create_column(cr, "stock_warn_insufficient_qty_scrap", "quantity", "float8")
    util.create_column(cr, "stock_warn_insufficient_qty_scrap", "product_uom_name", "varchar")

    views = """
        assets_common
        stock_inventory_line_tree2
        view_location_qweb
        stock_location_hierarchy
    """
    for view in util.splitlines(views):
        util.remove_view(cr, f"stock.{view}")
