# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # As we now generate 'work_hours' appointment category to last until 00:00 of the next day,
    # convert existing ones that were defined the old way (end_hour = 23:59)
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
            UPDATE appointment_slot s
            SET end_hour=0
            FROM appointment_type t
            WHERE s.end_hour>23.98 AND s.appointment_type_id=t.id AND t.category='work_hours'
            """,
            table="appointment_slot",
            alias="s",
        ),
    )

    util.change_field_selection_values(cr, "appointment.type", "category", {"work_hours": "anytime"})
