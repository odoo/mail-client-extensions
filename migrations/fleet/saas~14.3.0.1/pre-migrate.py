# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "fleet.vehicle.model", "manager_id")
    cr.execute("UPDATE fleet_vehicle_log_services SET state='new' WHERE state='todo'")
