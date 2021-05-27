# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "fleet_vehicle_model", "category_id", "int4")
    util.create_column(cr, "fleet_vehicle_model", "transmission", "varchar")

    util.create_column(cr, "fleet_vehicle", "trailer_hook", "bool", default=False)
