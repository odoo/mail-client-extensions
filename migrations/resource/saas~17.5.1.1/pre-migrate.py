from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "resource_calendar", "flexible_hours", "boolean")

    c_cols = util.get_columns(
        cr,
        "resource_calendar",
        ignore=("id", "name", "flexible_hours", "create_date", "write_date", "create_uid", "write_uid"),
    )

    # 1. Find all human resources with null calendar_id (flexible resources) and their corresponding company default calendar_id
    # 2. For each company with at least one flexible resource, create a default flexible calendar
    # 3. Update the calendar_id of all flexible resources to the new flexible calendar
    query = util.format_query(
        cr,
        """
        WITH companies AS (
            SELECT rc.id,
                   rc.resource_calendar_id default_calendar_id,
                   array_agg(rr.id) human_resource_ids
              FROM resource_resource rr
              JOIN res_company rc
                ON rr.company_id = rc.id
             WHERE rr.resource_type = 'user'
               AND rr.calendar_id IS NULL
          GROUP BY rc.id
        ), inserted_flex_calendars AS (
            INSERT INTO resource_calendar (name, flexible_hours, {cols})
            SELECT CONCAT(rc.name, ' (flexible)'), true, {rc_cols}
              FROM companies
              JOIN resource_calendar rc
                ON rc.id = companies.default_calendar_id
         RETURNING id, company_id
        )
        UPDATE resource_resource rr
           SET calendar_id = inserted_flex_calendars.id
          FROM companies
          JOIN inserted_flex_calendars
            ON companies.id = inserted_flex_calendars.company_id
         WHERE rr.id = ANY(companies.human_resource_ids)
        """,
        cols=c_cols,
        rc_cols=c_cols.using(alias="rc"),
    )
    cr.execute(query)

    # full_time_required_hours was defined in hr_payroll, we need to create the column
    # in case hr_payroll was not installed
    util.create_column(cr, "resource_calendar", "full_time_required_hours", "float8")
    cr.execute("""
      WITH cals AS (
          SELECT calendar_id,
                 ROUND(CAST(SUM(hour_to - hour_from) AS numeric), 1) AS total
            FROM resource_calendar_attendance
           WHERE day_period != 'lunch'
           GROUP BY calendar_id
     ) UPDATE resource_calendar c
          SET full_time_required_hours = cals.total
         FROM cals
        WHERE c.id = cals.calendar_id
          AND c.full_time_required_hours IS NULL
          AND c.flexible_hours IS NOT True
    """)
