# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # To satisfy the newly added constraint:
    # ((end_hour=0 AND (start_hour BETWEEN 0 AND 23.99))
    #   OR (start_hour BETWEEN 0 AND end_hour))
    # AND (end_hour=0
    #   OR (end_hour BETWEEN start_hour AND 23.99))

    def parallel_explode_execute_appointment_slot(query, alias=None):
        util.parallel_execute(cr, util.explode_query_range(cr, query, table="appointment_slot", alias=alias))

    # Squeezes interval start_hour, end_hour between 0 and 23.99 and enforces that start_hour <= end_hour
    # Note that 23.99 is a little above 23:59 which is the maximum value that the user can set in the interface
    parallel_explode_execute_appointment_slot(
        """
        UPDATE appointment_slot
           SET start_hour=LEAST(GREATEST(start_hour, 0), 23.99)
         WHERE start_hour NOT BETWEEN 0 AND 23.99
        """
    )
    parallel_explode_execute_appointment_slot(
        """
        UPDATE appointment_slot
           SET end_hour=LEAST(GREATEST(end_hour, start_hour), 23.99)
         WHERE end_hour NOT BETWEEN start_hour AND 23.99
        """
    )
    # Convert end_hour 23.99 (value we will get if the user has set 24 or greater in the interface) into 00:00 of next day
    parallel_explode_execute_appointment_slot("UPDATE appointment_slot SET end_hour=0 WHERE end_hour=23.99")
