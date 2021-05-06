# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "product_category", "packaging_reserve_method", "varchar", default="partial")
    util.create_column(cr, "product_packaging", "package_type_id", "int4")

    util.create_m2m(
        cr, "stock_location_route_packaging", "product_packaging", "stock_location_route", "packaging_id", "route_id"
    )

    util.create_column(cr, "stock_location_route", "packaging_selectable", "boolean")

    util.create_column(cr, "stock_move", "product_packaging_id", "int4")
