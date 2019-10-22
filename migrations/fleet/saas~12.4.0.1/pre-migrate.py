# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "fleet_vehicle", "future_driver_id", "int4")
    util.create_column(cr, "fleet_vehicle", "next_assignation_date", "date")
    util.create_column(cr, "fleet_vehicle", "net_car_value", "float8")
    util.create_column(cr, "fleet_vehicle", "plan_to_change_car", "boolean")
    util.create_column(cr, "fleet_vehicle_cost", "company_id", "int4")
    util.create_column(cr, "fleet_vehicle_model", "manager_id", "int4")
    util.create_column(cr, "res_partner", "plan_to_change_car", "boolean")

    # cr.execute("UPDATE res_partner SET plan_to_change_car=FALSE")
    # cr.execute("UPDATE fleet_vehicle SET plan_to_change_car=FALSE")
