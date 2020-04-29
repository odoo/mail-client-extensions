# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "generate.simulation.link", "car_id")
    util.remove_field(cr, "generate.simulation.link", "new_car")
    util.remove_field(cr, "generate.simulation.link", "customer_relation")
