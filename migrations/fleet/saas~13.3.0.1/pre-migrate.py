# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    if util.create_column(cr, "fleet_vehicle_log_services", "purchaser_id", "integer"):
        cr.execute(
            """
            UPDATE fleet_vehicle_log_services s
               SET purchaser_id = v.driver_id
              FROM fleet_vehicle v
             WHERE v.id = s.vehicle_id
        """
        )
