# -*- coding: utf-8 -*-
from odoo import fields
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    dt = fields.Datetime.from_string
    ResCal = util.env(cr)['resource.calendar']
    changes = [('working_hours_open', 'date_assign'), ('working_hours_close', 'date_end')]
    for hour, date in changes:
        # Note: < 36 seconds will give less than 0.1 hour
        cr.execute("""
            UPDATE project_task
               SET {0}=0
             WHERE {0} IS NULL
               AND create_date IS NOT NULL
               AND {1} IS NOT NULL
               AND {1} - create_date < interval '36 seconds'
        """.format(hour, date))

        cr.execute("""
            SELECT p.resource_calendar_id, t.id, t.create_date, t.{1}, pa.tz
              FROM project_task t
              JOIN project_project p ON (p.id = t.project_id)
              JOIN res_users u ON (u.id = t.user_id)
              JOIN res_partner pa ON (pa.id = u.partner_id)
             WHERE t.{0} IS NULL
               AND t.create_date IS NOT NULL
               AND t.{1} IS NOT NULL
               AND p.resource_calendar_id IS NOT NULL
        """.format(hour, date))
        for cid, tid, date_from, date_to, tz in cr.fetchall():
            cal = ResCal.browse(cid).with_context(tz=tz)
            value = cal.get_work_hours_count(dt(date_from), dt(date_to), None, compute_leaves=True)
            cr.execute("""
                UPDATE project_task
                   SET {} = %s
                 WHERE id=%s
            """.format(hour), [value, tid])

    cr.execute("""
        UPDATE project_task
           SET working_days_open = COALESCE(working_hours_open, 0) / 24,
               working_days_close = COALESCE(working_hours_close, 0) / 24
    """)
