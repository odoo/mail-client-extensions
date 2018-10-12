# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.ensure_xmlid_match_record(
        cr, "fleet.fleet_vehicle_state_new_request", "fleet.vehicle.state", {"name": "New Request"}
    )
    util.create_column(cr, "fleet_vehicle", "brand_id", "integer")
    cr.execute(
        """
        UPDATE fleet_vehicle v
        SET brand_id=m.brand_id
        FROM fleet_vehicle_model m
        WHERE v.model_id=m.id
    """
    )
