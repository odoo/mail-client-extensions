# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_contract", "wishlist_car_total_depreciated_cost", "float8")
    util.create_column(cr, "hr_contract", "transport_mode_bike", "boolean", default=False)
    util.create_column(cr, "hr_contract", "bike_id", "int4")
    util.create_column(cr, "hr_contract", "new_bike_model_id", "int4")
    util.create_column(cr, "hr_contract", "company_bike_depreciated_cost", "float8")
