# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

try:
    from odoo.tools.date_intervals import HOURS_PER_DAY
except ImportError:
    try:
        # < saas-18.2
        from odoo.addons.resource.models.utils import HOURS_PER_DAY
    except ImportError:
        try:
            # < saas-16.1
            from odoo.addons.resource.models.resource import HOURS_PER_DAY
        except ImportError:
            # < saas-11.2
            from odoo.addons.hr_holidays.models.hr_holidays import HOURS_PER_DAY


def migrate(cr, version):
    pv = util.parse_version

    # The name generation fix odoo/odoo#45292 was applied from 11.0 to saas~13.3
    # However, 14.0 has already been released when this has been written
    # The same goes for the leaves sharing the same meeting id: duplicating a lead is forbidden since odoo/odoo#21477 (saas~11.1).
    # Since nothing fixed it in migrations, it is possible that databases up to 14.0 have problematic data.
    # Therefore, we need to patch any migration if the source version is <= 14.0
    # and if the target version is >= 11.0
    if pv(version) < pv("saas~14.1") and util.version_gte("11.0"):
        env = util.env(cr)
        # base.user_admin exists only since 12.0
        user_admin = env.ref("base.user_admin", raise_if_not_found=False) or env.ref("base.user_root")

        # hr.leave was hr.holidays before saas-11.3
        HrLeave = env.get("hr.leave", env.get("hr.holidays"))
        hr_leave_name = HrLeave._table

        # Before 11.0, hr.leaves could be duplicated, and the link to the meeting_id was copied too
        # Therefore we need to create new calendar.events for hr.leaves that share the same meeting_id
        query = util.format_query(
            cr,
            """SELECT ce.id
                 FROM calendar_event ce
                 JOIN {hr_leave} hl on ce.id = hl.meeting_id
             GROUP BY ce.id
               HAVING COUNT(*) > 1
            """,
            hr_leave=hr_leave_name,
        )
        cr.execute(query)
        shared_event_ids = tuple(i[0] for i in env.cr.fetchall())

        if shared_event_ids:
            # resource.calendar:hours_per_day exists since saas~11.2
            if "hours_per_day" in env["resource.calendar"]:
                hours_per_day_expr = "COALESCE(rc.hours_per_day, %(default_hours_per_day)s)"
                hours_per_day_join = """
                    LEFT JOIN hr_employee he ON he.id = hl.employee_id
                    LEFT JOIN resource_resource res ON res.id = he.resource_id
                    LEFT JOIN resource_calendar rc ON rc.id = COALESCE(res.calendar_id, %(company_calendar_id)s)"""
            # before saas~11.2, fallback to the default daily hours
            else:
                hours_per_day_expr = "%(default_hours_per_day)s"
                hours_per_day_join = ""

            # calendar.event:event_tz exists since saas~12.4 and is computed since 14.0
            if "event_tz" in env["calendar.event"]._fields and env["calendar.event"]._fields["event_tz"].store:
                event_tz_update_expr = ", event_tz = rp.tz"
                event_tz_insert_column = "event_tz, "
                event_tz_insert_expr = "rp.tz, "
                event_tz_join = """
                    LEFT JOIN res_users ru ON ru.id = hl.user_id
                    LEFT JOIN res_partner rp ON rp.id = ru.partner_id"""
            # before saas~12.4, no need to update or insert this column
            else:
                event_tz_update_expr = ""
                event_tz_insert_column = ""
                event_tz_insert_expr = ""
                event_tz_join = ""

            # calendar.event:state does not exist since 14.0
            if "state" in env["calendar.event"]._fields:
                state_update_expr = ", state = 'open'"
                state_insert_column = "state, "
                state_insert_expr = "'open', "
            # since 14.0, no need to update or insert this column
            else:
                state_update_expr = ""
                state_insert_column = ""
                state_insert_expr = ""

            # Update the calendar events to the data of the oldest of its hr.leaves
            env.cr.execute(
                """UPDATE calendar_event ce
                      SET duration = hl.number_of_days * {hours_per_day},
                          description = hl.notes,
                          user_id = hl.user_id,
                          start = hl.date_from,
                          allday = false
                          {state_expr},
                          privacy = 'confidential'
                          {event_tz_expr}
                     FROM {hr_leave} hl
                          {hours_per_day_join}
                          {event_tz_join}
                    WHERE hl.meeting_id IN %(shared_event_ids)s
                      AND ce.id = hl.meeting_id
                      AND NOT EXISTS(SELECT 1
                                       FROM {hr_leave} hl2
                                      WHERE hl2.meeting_id = hl.meeting_id
                                        AND hl2.id > hl.id)""".format(
                    event_tz_expr=event_tz_update_expr,
                    event_tz_join=event_tz_join,
                    hours_per_day=hours_per_day_expr,
                    hours_per_day_join=hours_per_day_join,
                    hr_leave=hr_leave_name,
                    state_expr=state_update_expr,
                ),
                {
                    "default_hours_per_day": HOURS_PER_DAY,
                    "company_calendar_id": user_admin.company_id.resource_calendar_id.id,
                    "shared_event_ids": shared_event_ids,
                },
            )

            # Create calendar events for the other hr.leaves and fix the foreign keys
            # As the name is recomputed in the following query, store the hl.id in it, in order to be able to
            # update the foreign key in the second WITH clause
            env.cr.execute(
                """WITH t AS (INSERT INTO calendar_event (name, duration, description, user_id, start,
                                                          stop, allday, {state_column} privacy, {event_tz_column} show_as)
                                   SELECT hl.id,
                                          hl.number_of_days * {hours_per_day},
                                          hl.notes,
                                          hl.user_id,
                                          hl.date_from,
                                          hl.date_to,
                                          false,
                                          {state_expr}
                                          'confidential',
                                          {event_tz_expr}
                                          'busy'
                                     FROM {hr_leave} hl
                                          {hours_per_day_join}
                                          {event_tz_join}
                                    WHERE hl.meeting_id in %(shared_event_ids)s
                                      AND EXISTS(SELECT 1
                                                   FROM {hr_leave} hl2
                                                  WHERE hl2.meeting_id = hl.meeting_id
                                                    AND hl2.id > hl.id)
                                RETURNING id ce_id, name::int hl_id
                             ),
                        u AS (
                                 UPDATE {hr_leave} hl
                                    SET meeting_id = t.ce_id
                                   FROM t
                                  WHERE hl.id = t.hl_id
                              RETURNING t.ce_id, t.hl_id
                             )
                   INSERT INTO calendar_event_res_partner_rel (calendar_event_id, res_partner_id)
                        SELECT u.ce_id,
                               rp.id
                          FROM u
                          JOIN {hr_leave} hl on hl.id = u.hl_id
                          JOIN res_users ru on ru.id = hl.user_id
                          JOIN res_partner rp on rp.id = ru.partner_id""".format(
                    event_tz_column=event_tz_insert_column,
                    event_tz_expr=event_tz_insert_expr,
                    event_tz_join=event_tz_join,
                    hours_per_day=hours_per_day_expr,
                    hours_per_day_join=hours_per_day_join,
                    hr_leave=hr_leave_name,
                    state_column=state_insert_column,
                    state_expr=state_insert_expr,
                ),
                {
                    "default_hours_per_day": HOURS_PER_DAY,
                    "company_calendar_id": user_admin.company_id.resource_calendar_id.id,
                    "shared_event_ids": shared_event_ids,
                },
            )

        # The calendar.event is created from the hr.leave in the hr.leave:action_validate call
        # Therefore the language of the name of the event will be the one of the person who validates, which does not add much sense
        # As a shortcut, we will use the language of the admin user.
        meeting_name_days_fmt = (
            env["ir.translation"]
            ._get_source(None, ("code",), user_admin.lang, "%s on Time Off : %.2f day(s)")
            .replace("%.2f", "%s")
        )
        meeting_name_hours_fmt = (
            env["ir.translation"]
            ._get_source(None, ("code",), user_admin.lang, "%s on Time Off : %.2f hour(s)")
            .replace("%.2f", "%s")
        )

        # hr.leave.type was hr.holidays.status up to saas-11.3
        HrLeaveType = env.get("hr.leave.type", env.get("hr.holidays.status"))
        hr_leave_type_name = HrLeaveType._table

        # field request_unit did not exist before 12.0; request_unit was days by then
        if "request_unit" in HrLeaveType:
            new_name_expr = """(CASE WHEN hlt.request_unit = 'hour'
                          THEN FORMAT(%(meeting_name_hours_fmt)s, COALESCE(he.name, hec.name),
                                      TO_CHAR(COALESCE(hl.number_of_days, 0)
                                                * COALESCE(emp_cal.hours_per_day, comp_cal.hours_per_day),
                                              'FM9999999990.00'))
                          WHEN hlt.request_unit = 'half'
                          THEN FORMAT(%(meeting_name_days_fmt)s, COALESCE(he.name, hec.name),
                                      TO_CHAR(COALESCE(hl.number_of_days, 0) * 2, 'FM9999999990.00'))
                          ELSE FORMAT(%(meeting_name_days_fmt)s, COALESCE(he.name, hec.name),
                                      TO_CHAR(COALESCE(hl.number_of_days, 0), 'FM9999999990.00'))
                     END)"""
        else:
            new_name_expr = """FORMAT(%(meeting_name_days_fmt)s, COALESCE(he.name, hec.name),
                                      TO_CHAR(COALESCE(hl.number_of_days, 0), 'FM9999999990.00'))"""

        # Hide the type of leave from the name of the calendar events, as it is a confidential information
        # Ignore the ones that match an existing translation
        query = (
            r"""
           UPDATE calendar_event ce
              SET name = {new_name_expr}
             FROM {hr_leave} hl
             JOIN {hr_leave_type} hlt ON hl.holiday_status_id = hlt.id
        LEFT JOIN hr_employee_category hec ON hl.category_id = hec.id
        LEFT JOIN hr_employee he ON hl.employee_id = he.id
        LEFT JOIN resource_resource emp_res ON he.resource_id = emp_res.id
        LEFT JOIN resource_calendar emp_cal ON emp_res.calendar_id = emp_cal.id
        LEFT JOIN resource_calendar comp_cal ON comp_cal.id = %(company_calendar_id)s
            WHERE hl.meeting_id = ce.id
              AND NOT EXISTS (
                    SELECT 1
                      FROM (
                                  SELECT lang, value,
                                         regexp_replace(regexp_replace(value, '[|*+()[\]\\%%_]', '\\\&', 'g'),
                                                        '\\%%s|\\%%.2f', '%%', 'g') pattern
                                    FROM ir_translation
                                   WHERE type = 'code'
                                     AND (
                                             (MD5(src) = MD5('%%s on Time Off : %%.2f day(s)')
                                              AND src = '%%s on Time Off : %%.2f day(s)')
                                          OR (MD5(src) = MD5('%%s on Time Off : %%.2f hour(s)')
                                              AND src = '%%s on Time Off : %%.2f hour(s)')
                                         )
                            UNION SELECT 'en_US','%%s on Time Off : %%.2f day(s)','%% on Time Off : %% day\(s\)'
                            UNION SELECT 'en_US','%%s on Time Off : %%.2f hour(s)','%% on Time Off : %% hour\(s\)'
                           ) it
                     WHERE ce.name SIMILAR TO it.pattern
                  )"""
        ).format(hr_leave=hr_leave_name, hr_leave_type=hr_leave_type_name, new_name_expr=new_name_expr)

        params = {
            "meeting_name_days_fmt": meeting_name_days_fmt,
            "meeting_name_hours_fmt": meeting_name_hours_fmt,
            "company_calendar_id": user_admin.company_id.resource_calendar_id.id,
        }
        env.cr.execute(query, params)
