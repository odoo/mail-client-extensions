from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "calendar_recurrence", "trigger_id", "int4")
    cron_id = util.ref(cr, "calendar.ir_cron_scheduler_alarm")
    if cron_id:
        # We delete existing cron trigger because one cron was created by event, sometimes several time per event because
        # the end_date was modified
        cr.execute("DELETE FROM ir_cron_trigger WHERE cron_id=%s", [cron_id])
        # Create ir.cron.trigger:
        # - for recurring events, we only save one cron trigger per event. The next
        # - non recurring events will have all their trigger created at once.
        cr.execute(
            """
                WITH info AS (
                 SELECT DISTINCT ON (rec.id, call_at)
                        rec.id AS rec_id, -- null for non-recurring events
                        min(e.start - make_interval(mins => a.duration_minutes)) AS call_at
                   FROM calendar_event e
                   JOIN calendar_alarm_calendar_event_rel ral
                     ON ral.calendar_event_id = e.id
                   JOIN calendar_alarm a
                     ON a.id = ral.calendar_alarm_id
                     -- create one trigger per recurrence or per non-recurring event
              LEFT JOIN calendar_recurrence rec
                     ON rec.id = e.recurrence_id
                  WHERE a.alarm_type IN ('email', 'sms')
                     -- do not create a trigger in the past
                    AND e.start - make_interval(mins => a.duration_minutes) > CURRENT_DATE
               GROUP BY coalesce(rec.id, a.id), rec.id
            ),
            info_per_date AS (
                -- uniquify per date to avoid duplicated triggers
                SELECT ARRAY_AGG(rec_id) AS ids,
                       call_at
                  FROM info
                 GROUP BY call_at
            ),
            new_triggers AS (
                 INSERT INTO ir_cron_trigger(cron_id, call_at)
                 SELECT %s AS cron_id,
                        info_per_date.call_at AS call_at
                   FROM info_per_date
              RETURNING id, call_at
            )
            UPDATE calendar_recurrence rec
               SET trigger_id = new_triggers.id
              FROM info_per_date
              JOIN new_triggers
             USING (call_at)
             WHERE rec.id = ANY(info_per_date.ids)
            """,
            [cron_id],
        )
