from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "resource_calendar_attendance", "duration_hours", "float8")
    query = """
        UPDATE resource_calendar_attendance
           SET duration_hours =
              CASE
                WHEN day_period != 'lunch' THEN hour_to - hour_from
                ELSE 0
              END
         WHERE day_period != 'lunch'
    """
    util.explode_execute(cr, query, table="resource_calendar_attendance")

    util.remove_field(cr, "resource.calendar.attendance", "date_from")
    util.remove_field(cr, "resource.calendar.attendance", "date_to")
    util.remove_field(cr, "resource.calendar.attendance", "resource_id")
