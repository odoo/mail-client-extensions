# -*- coding: utf-8 -*-
import itertools

from odoo.addons.resource.models.utils import HOURS_PER_DAY

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.leave", "report_note")

    util.create_column(cr, "hr_leave_allocation", "number_of_hours_display", "float8")
    queries = [
        cr.mogrify(query, [HOURS_PER_DAY]).decode()
        for query in [
            """
            UPDATE hr_leave_allocation a
               SET number_of_hours_display = a.number_of_days * COALESCE(rc.hours_per_day, %s)
              FROM hr_employee e
         LEFT JOIN resource_calendar rc
                ON e.resource_calendar_id = rc.id
             WHERE a.holiday_type = 'employee' AND a.employee_id = e.id
            """,
            """
            UPDATE hr_leave_allocation a
               SET number_of_hours_display = a.number_of_days * COALESCE(rc.hours_per_day, %s)
              FROM hr_leave_type lt
         LEFT JOIN res_company c
                ON c.id = lt.company_id
         LEFT JOIN resource_calendar rc
                ON c.resource_calendar_id = rc.id
             WHERE a.holiday_type != 'employee' AND a.holiday_status_id = lt.id
            """,
        ]
    ]

    util.parallel_execute(
        cr,
        list(
            itertools.chain.from_iterable(
                util.explode_query_range(cr, query, "hr_leave_allocation", alias="a") for query in queries
            )
        ),
    )
