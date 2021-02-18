# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "fleet_vehicle", "first_contract_date", "date")
    util.remove_constraint(cr, "fleet_vehicle", "fleet_vehicle_driver_id_unique")
