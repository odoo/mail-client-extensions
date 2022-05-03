# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.change_field_selection_values(
        cr, "fleet.vehicle.model", "default_fuel_type", {"hybrid": "full_hybrid", "full_hybrid_gasoline": "full_hybrid"}
    )
    util.change_field_selection_values(
        cr, "fleet.vehicle", "fuel_type", {"hybrid": "full_hybrid", "full_hybrid_gasoline": "full_hybrid"}
    )
