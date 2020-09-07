# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

    util.create_column(cr, "generate_simulation_link", "new_car", "boolean")
    util.create_column(cr, "generate_simulation_link", "car_id", "int4")
