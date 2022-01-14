# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    util.rename_xmlid(cr, "stock.access_stock_production_lot", "stock.access_stock_lot")
    util.rename_model(cr, "stock.production.lot", "stock.lot")

    util.rename_model(cr, "stock.location.route", "stock.route")
    cr.execute("ALTER TABLE stock_location_route_categ RENAME TO stock_route_categ")
    cr.execute("ALTER TABLE stock_location_route_packaging RENAME TO stock_route_packaging")
    cr.execute("ALTER TABLE stock_location_route_move RENAME TO stock_route_move")

    util.rename_field(cr, "stock.rule", "location_id", "location_dest_id")

    util.rename_field(cr, "stock.move.line", "product_uom_qty", "reserved_uom_qty")
    util.rename_field(cr, "stock.move.line", "product_qty", "reserved_qty")

    util.create_column(cr, "stock_quant_package", "pack_date", "date")
    query = "UPDATE stock_quant_package SET pack_date = create_date"
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="stock_quant_package"))
