# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "fleet_vehicle_assignation_log", "driver_employee_id", "int4")

    cr.execute(
        """
            UPDATE fleet_vehicle_assignation_log log
               SET driver_employee_id = emp.id
              FROM hr_employee emp
             WHERE emp.address_home_id = log.driver_id
        """
    )
