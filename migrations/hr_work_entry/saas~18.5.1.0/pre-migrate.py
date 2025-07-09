from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_work_entry", "date", "date")

    # hr_work_entry_contact was merged into hr_work_entry in 18.4, the former could be uninstalled
    if util.column_exists(cr, "hr_work_entry", "version_id"):
        version_join = util.SQLStr("w.version_id = v.id")
        version_field = util.ColumnList.from_unquoted(cr, ["version_id"])
    else:
        version_join = util.SQLStr("False")
        version_field = util.ColumnList.from_unquoted(cr, [])

    # First, split all the work entries spanning over several localized days
    cr.execute(
        util.format_query(
            cr,
            """
        WITH multi_day_entries AS (
        -- pick multi day-entries, compute dates in right TZ
            SELECT w.id,
                   date_start AT TIME ZONE COALESCE(c1.tz, c2.tz, 'UTC') AS date_start,
                   date_stop AT TIME ZONE COALESCE(c1.tz, c2.tz, 'UTC') AS date_stop,
                   (date_start AT TIME ZONE COALESCE(c1.tz, c2.tz, 'UTC'))::date AS start_local_date,
                   (date_stop AT TIME ZONE COALESCE(c1.tz, c2.tz, 'UTC'))::date AS stop_local_date
              FROM hr_work_entry w
              LEFT JOIN hr_version v
                ON {version_join}
              LEFT JOIN resource_calendar c1
                ON v.resource_calendar_id = c1.id
              LEFT JOIN res_company c
                ON v.company_id = c.id
              LEFT JOIN resource_calendar c2
                ON c.resource_calendar_id = c2.id
             WHERE (date_start AT TIME ZONE COALESCE(c1.tz, c2.tz, 'UTC'))::date
                   <
                   (date_stop AT TIME ZONE COALESCE(c1.tz, c2.tz, 'UTC'))::date
        ),
        -- generated one entry per day, for multi-day entries
        expanded_entries AS (
            SELECT mde.id,
                   gs.day AS local_date,
                   mde.start_local_date,
                   mde.stop_local_date,
                   EXTRACT(EPOCH FROM
                       -- pick the min from end of current day and date_stop
                       LEAST(gs.day + INTERVAL '1 day', mde.date_stop)
                       -- pick the max from start of current day and date_start
                     - GREATEST(gs.day, mde.date_start)
                   ) / 3600 AS day_duration
              FROM multi_day_entries mde,
                   generate_series(
                       mde.start_local_date,
                       mde.stop_local_date,
                       INTERVAL '1 day'
                   ) AS gs(day)
        ),
        -- create the entry from the generated data, with rigth day_duration
        inserted AS (
            INSERT INTO hr_work_entry (
                        name, employee_id {version_field}, work_entry_type_id,
                        company_id, "date",
                        duration,
                        date_start, date_stop
                        )
                 SELECT w.name, w.employee_id {version_field_w}, w.work_entry_type_id,
                        w.company_id, ee.local_date,
                        (ee.day_duration / SUM(ee.day_duration) OVER (PARTITION BY ee.id)) * w.duration,
                        ee.start_local_date, ee.stop_local_date
                   FROM expanded_entries ee
                   JOIN hr_work_entry w
                     ON ee.id = w.id
        )
        -- remove the former multi-day entries
        DELETE FROM hr_work_entry we
              USING multi_day_entries
              WHERE we.id = multi_day_entries.id
    """,
            version_field=version_field.using(leading_comma=True),
            version_field_w=version_field.using(alias="w", leading_comma=True),
            version_join=version_join,
        )
    )
    # Second, set date where it's not specified yet by taking the localized date_start
    cr.execute(
        util.format_query(
            cr,
            """
            UPDATE hr_work_entry w_upg
               SET "date" = (w.date_start AT TIME ZONE COALESCE(c1.tz, c2.tz, 'UTC'))::date
              FROM hr_work_entry w
         LEFT JOIN hr_version v
                ON {version_join}
         LEFT JOIN resource_calendar c1
                ON v.resource_calendar_id = c1.id
         LEFT JOIN res_company c
                ON v.company_id = c.id
         LEFT JOIN resource_calendar c2
                ON c.resource_calendar_id = c2.id
             WHERE w.id = w_upg.id
               AND w.date_start IS NOT NULL
    """,
            version_join=version_join,
        )
    )

    # Third, regroup all the similar work entries, aka same
    # date, work_entry_type_id, employee_id, version_id, company_id

    # Update row we'll keep with total duration
    cr.execute(
        util.format_query(
            cr,
            """
        WITH merged AS (
            SELECT ARRAY_AGG(id ORDER BY id) AS ids,
                   "date",
                   work_entry_type_id,
                   employee_id,
                   company_id,
                    SUM(duration) as total_duration
                   {version_field}
              FROM hr_work_entry
          GROUP BY "date", work_entry_type_id, employee_id {version_field}, company_id
            HAVING COUNT(*) > 1
        ), _upd AS (
            UPDATE hr_work_entry hwe
               SET duration = merged.total_duration
              FROM merged
             WHERE hwe.id = merged.ids[1]
        )
        -- Delete duplicate rows
        DELETE FROM hr_work_entry hwe
              USING merged
              WHERE hwe.id = ANY(merged.ids[2:])
    """,
            version_field=version_field.using(leading_comma=True),
        )
    )

    # Last, remove datetime fields once for all
    util.remove_field(cr, "hr.work.entry.report", "date_start")
    util.remove_field(cr, "hr.work.entry", "date_start", cascade=True)
    util.remove_field(cr, "hr.work.entry", "date_stop", cascade=True)
