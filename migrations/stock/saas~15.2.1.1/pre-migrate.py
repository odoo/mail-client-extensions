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
