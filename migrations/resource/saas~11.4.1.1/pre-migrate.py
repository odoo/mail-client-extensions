# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "resource_calendar_attendance", "day_period", "varchar")
    cr.execute("""
        UPDATE resource_calendar_attendance
           SET day_period= CASE WHEN hour_from >= 12 THEN 'afternoon'
                                ELSE 'morning'
                            END
    """)

    util.create_column(cr, "resource_calendar", "tz", "varchar")
    cr.execute("UPDATE resource_calendar SET tz='UTC' WHERE tz IS NULL")
    util.create_column(cr, "resource_resource", "tz", "varchar")
    cr.execute("""
        UPDATE resource_resource r
           SET tz=COALESCE(p.tz, 'UTC')
          FROM res_users u JOIN res_partner p ON (u.partner_id = p.id)
         WHERE u.id = r.user_id
           AND r.tz IS NULL
    """)
    cr.execute("UPDATE resource_resource SET tz='UTC' WHERE tz IS NULL")

    util.remove_field(cr, "resource_calendar_leaves", "tz")