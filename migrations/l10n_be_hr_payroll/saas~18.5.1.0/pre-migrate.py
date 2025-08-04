from collections import defaultdict

from odoo.upgrade import util


def migrate_part_time_calendars(cr):
    cr.execute(
        """
          SELECT v.id,
                 com.resource_calendar_id,
                 v.resource_calendar_id,
                 v.time_credit_type_id
            FROM hr_version v
            JOIN res_company com
              ON v.company_id = com.id
            JOIN res_partner p
              ON com.partner_id = p.id
            JOIN res_country cou
              ON p.country_id = cou.id
           WHERE v.time_credit = TRUE
             AND v.time_credit_type_id IS NOT NULL
             AND cou.code = 'BE'
        ORDER BY v.id
        """
    )

    if not cr.rowcount:
        return

    time_credit_be_versions = {
        version_id: (company_calendar, version_calendar, work_entry_type)
        for version_id, company_calendar, version_calendar, work_entry_type in cr.fetchall()
    }

    all_calendars = {
        calendar
        for company_calendar, version_calendar, _ in time_credit_be_versions.values()
        for calendar in (company_calendar, version_calendar)
    }

    cr.execute(
        """
          SELECT id, calendar_id, dayofweek, day_period, hour_from, hour_to
            FROM resource_calendar_attendance
           WHERE calendar_id IN %s
        ORDER BY id
        """,
        [tuple(all_calendars)],
    )
    attendance_lines_by_calendar_with_id = defaultdict(set)
    attendance_lines_by_calendar = defaultdict(set)
    for id, calendar_id, dayofweek, day_period, hour_from, hour_to in cr.fetchall():
        attendance_lines_by_calendar_with_id[calendar_id].add((id, dayofweek, day_period, hour_from, hour_to))
        attendance_lines_by_calendar[calendar_id].add((dayofweek, day_period, hour_from, hour_to))

    # To avoid creating one new calendar per version, we group them by company, calendar and work_entry_type
    grouped = defaultdict(list)
    for version_id, (company_calendar, version_calendar, time_credit_type_id) in time_credit_be_versions.items():
        grouped[(company_calendar, version_calendar, time_credit_type_id)].append(version_id)

    versions_no_calendar_migration = []
    for (company_calendar, version_calendar, time_credit_type_id), version_ids in grouped.items():
        # Here, we must duplicate the version calendar and complete it to match the company calendar.
        # The added lines must be of time_credit_type_id type. If the two calendars do not match, do nothing.
        version_attendance_lines = attendance_lines_by_calendar[version_calendar]
        company_attendance_lines = attendance_lines_by_calendar[company_calendar]
        if not version_attendance_lines <= company_attendance_lines:
            # If the time credit's calendar is not a subset of the company's calendar, then it becomes quite complicated
            # to guess which credit time records to add to match the default working schedule. In this case, add a
            # warning to the upgrade report for manual upgrade.
            versions_no_calendar_migration.extend((v_id, time_credit_type_id) for v_id in version_ids)
            continue
        # Duplicate the version's calendar
        columns = util.get_columns(cr, "resource_calendar")
        cr.execute(
            util.format_query(
                cr,
                """
                INSERT INTO resource_calendar({columns})
                     SELECT {columns}
                       FROM resource_calendar
                      WHERE id = %s
                  RETURNING id
                """,
                columns=columns,
            ),
            [version_calendar],
        )
        new_calendar_id = cr.fetchone()

        # Duplicate attendance lines
        attendance_lines_columns = util.get_columns(cr, "resource_calendar_attendance", ignore=("id", "calendar_id"))
        cr.execute(
            util.format_query(
                cr,
                """
                INSERT INTO resource_calendar_attendance({columns}, calendar_id)
                     SELECT {columns}, %s
                       FROM resource_calendar_attendance
                      WHERE id = ANY(%s)
                """,
                columns=attendance_lines_columns,
            ),
            [new_calendar_id, [a[0] for a in attendance_lines_by_calendar_with_id[version_calendar]]],
        )
        # Add the missing attendance lines
        for to_add_attendance in company_attendance_lines - version_attendance_lines:
            dayofweek, day_period, hour_from, hour_to = to_add_attendance
            cr.execute(
                """
                INSERT INTO resource_calendar_attendance (calendar_id, name, dayofweek, day_period, hour_from, hour_to, work_entry_type_id)
                     VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                [new_calendar_id, "Time credit", dayofweek, day_period, hour_from, hour_to, time_credit_type_id],
            )
        cr.execute(
            "UPDATE hr_version SET resource_calendar_id = %s WHERE id IN %s",
            [new_calendar_id, tuple(version_ids)],
        )
    if versions_no_calendar_migration:
        version_links = " ".join(
            "<li>{} - {}</li>".format(
                util.get_anchor_link_to_record("hr.version", version_id, None),
                util.get_anchor_link_to_record("hr.work.entry.type", time_credit_type_id, None),
            )
            for version_id, time_credit_type_id in versions_no_calendar_migration
        )
        message = """
            <details>
                <summary>
                    <strong>Warning:</strong> Some part time versions need manual working schedule upgrade<br>
                    It concerns only Belgian versions which are tagged as Time Credit, Parental or Partial Incapacity part time contracts.

                    This may cause issues with payroll processing and work entries generation.
                    Below you can find a list of the affected records, with their complementary work entry type.
                    To fix them, you need to complete their working schedule so that for each "part time" period,
                    you add an attendance line with the correct corresponding part time work entry type.
                </summary>
                <ul>{}</ul>
            </details>
        """.format(version_links)
        util.add_to_migration_reports(message=message, category="Payroll", format="html")


def migrate(cr, version):
    util.remove_view(cr, "l10n_be_hr_payroll.hr_payslip_run_view_form")
    util.remove_field(cr, "hr.payslip.employee.depature.holiday.attests", "unpaid_average_remunaration_n1")
    util.remove_field(cr, "hr.payslip.employee.depature.holiday.attests", "unpaid_average_remunaration_n")
    util.remove_field(cr, "hr.payslip.employee.depature.holiday.attests", "unpaid_time_off_n1")
    util.remove_field(cr, "hr.payslip.employee.depature.holiday.attests", "unpaid_time_off_n")
    util.remove_field(cr, "hr.payslip.employee.depature.holiday.attests", "time_off_allocated")
    util.remove_field(cr, "hr.payslip.employee.depature.holiday.attests", "time_off_taken")
    util.remove_field(cr, "hr.payslip.employee.depature.holiday.attests", "time_off_allocation_n_ids")
    util.remove_field(cr, "hr.payslip.employee.depature.holiday.attests", "time_off_n_ids")
    util.remove_field(cr, "res.users", "spouse_fiscal_status")
    util.remove_field(cr, "res.users", "spouse_fiscal_status_explanation")
    util.remove_field(cr, "res.users", "disabled")
    util.remove_field(cr, "res.users", "disabled_spouse_bool")
    util.remove_field(cr, "res.users", "disabled_children_bool")
    util.remove_field(cr, "res.users", "disabled_children_number")
    util.remove_field(cr, "res.users", "dependent_children")
    util.remove_field(cr, "res.users", "other_dependent_people")
    util.remove_field(cr, "res.users", "other_senior_dependent")
    util.remove_field(cr, "res.users", "other_disabled_senior_dependent")
    util.remove_field(cr, "res.users", "other_juniors_dependent")
    util.remove_field(cr, "res.users", "other_disabled_juniors_dependent")
    util.remove_field(cr, "res.users", "dependent_seniors")
    util.remove_field(cr, "res.users", "dependent_juniors")
    util.remove_field(cr, "res.users", "l10n_be_scale_seniority")

    util.remove_view(cr, "l10n_be_hr_payroll.res_users_view_form")

    util.remove_field(cr, "l10n_be.hr.payroll.schedule.change.wizard", "part_time")
    util.remove_field(cr, "l10n_be.hr.payroll.schedule.change.wizard", "presence_work_entry_type_id")
    util.remove_field(cr, "l10n_be.hr.payroll.schedule.change.wizard", "absence_work_entry_type_id")

    migrate_part_time_calendars(cr)
