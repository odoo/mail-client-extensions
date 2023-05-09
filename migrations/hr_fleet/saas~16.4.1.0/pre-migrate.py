# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.delete_unused(cr, "hr_fleet.onboarding_fleet_training")

    util.explode_execute(
        cr,
        """
            UPDATE fleet_vehicle v
               SET driver_id = e.work_contact_id
              FROM hr_employee e
             WHERE v.driver_id = e.address_home_id
        """,
        table="fleet_vehicle",
        alias="v",
    )

    util.explode_execute(
        cr,
        """
            UPDATE fleet_vehicle v
               SET future_driver_id = e.work_contact_id
              FROM hr_employee e
             WHERE v.future_driver_id = e.address_home_id
        """,
        table="fleet_vehicle",
        alias="v",
    )

    util.explode_execute(
        cr,
        """
            UPDATE fleet_vehicle_assignation_log l
               SET driver_id = e.work_contact_id
              FROM hr_employee e
             WHERE l.driver_id = e.address_home_id
        """,
        table="fleet_vehicle_assignation_log",
        alias="l",
    )

    util.explode_execute(
        cr,
        """
            UPDATE fleet_vehicle_log_services s
               SET purchaser_id = e.work_contact_id
              FROM hr_employee e
             WHERE s.purchaser_id = e.address_home_id
        """,
        table="fleet_vehicle_log_services",
        alias="s",
    )
