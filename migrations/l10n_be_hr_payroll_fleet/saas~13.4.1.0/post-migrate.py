# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.recompute_fields(cr, "hr.contract", ["wishlist_car_total_depreciated_cost"])
