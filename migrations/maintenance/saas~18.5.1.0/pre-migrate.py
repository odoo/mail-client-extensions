from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "maintenance_request", "schedule_end", "timestamp without time zone")
    util.explode_execute(
        cr,
        """
        UPDATE maintenance_request
           SET duration = 1
         WHERE COALESCE(duration, 0) <= 0
        """,
        table="maintenance_request",
    )
    util.explode_execute(
        cr,
        """
        UPDATE maintenance_request
           SET schedule_end = schedule_date::timestamp without time zone + (duration || ' hour')::interval
        """,
        table="maintenance_request",
    )
