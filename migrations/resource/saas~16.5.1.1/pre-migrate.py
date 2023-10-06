from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "resource_calendar_attendance", "duration_days", "float8")
    query = """
            UPDATE resource_calendar_attendance
               SET duration_days = CASE
                                       WHEN day_period = 'lunch' THEN 0
                                       WHEN day_period != 'lunch' AND (hour_to - hour_from) <= rc.hours_per_day * 3 / 4 THEN 0.5
                                       ELSE 1
                                   END
              FROM resource_calendar rc
             WHERE resource_calendar_attendance.calendar_id = rc.id
            """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="resource_calendar_attendance"))
