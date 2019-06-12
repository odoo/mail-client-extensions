# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        WITH cala AS (
            SELECT calendar_id, SUM(hour_to - hour_from) AS hour_count, array_length(array_agg(DISTINCT dayofweek), 1) as len_dayofweek
                FROM resource_calendar_attendance
               WHERE date_from IS NULL AND date_to IS NULL
             GROUP BY calendar_id
            )
            UPDATE resource_calendar cal
              SET hours_per_day = cala.hour_count / cala.len_dayofweek
             FROM cala
            WHERE cal.id = cala.calendar_id
    """)
