# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "stock_location", "replenish_location", "boolean")
    query = """
        UPDATE stock_location l
           SET replenish_location = true
          FROM stock_warehouse w
         WHERE l.id = w.lot_stock_id
           AND l.usage = 'internal'
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="stock_location", alias="l"))
    util.create_column(cr, "stock_location", "warehouse_id", "int4")

    query = """
        UPDATE stock_location l
           SET warehouse_id = w.id
          FROM stock_warehouse w
          JOIN stock_location sl ON sl.id = w.view_location_id
         WHERE l.parent_path LIKE sl.parent_path || '%'
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="stock_location", alias="l"))
    util.remove_view(cr, "stock.stock_report_view_search")
    util.remove_menus(
        cr,
        [
            util.ref(cr, "stock.stock_move_menu"),
            util.ref(cr, "stock.menu_forecast_inventory"),
        ],
    )
    util.remove_record(cr, "stock.stock_move_action")
    util.remove_record(cr, "stock.report_stock_quantity_action")
    util.remove_record(cr, "stock.report_stock_quantity_action_product")

    util.remove_field(cr, "res.config.settings", "stock_mail_confirmation_template_id")

    util.create_column(cr, "stock_move", "quantity_done", "float8")
