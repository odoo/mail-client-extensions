from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.5")
class TestPartTime(UpgradeCase):
    def prepare(self):
        if not util.version_gte("saas~18.4"):
            return None

        company = self.env["res.company"].create(
            {
                "name": "Belgian Company",
                "country_id": self.env.ref("base.be").id,
            }
        )

        company_calendar_attendance_ids = [
            (
                0,
                0,
                {"name": "Monday Morning", "dayofweek": "0", "hour_from": 8, "hour_to": 12, "day_period": "morning"},
            ),
            (
                0,
                0,
                {
                    "name": "Monday Afternoon",
                    "dayofweek": "0",
                    "hour_from": 13,
                    "hour_to": 17,
                    "day_period": "afternoon",
                },
            ),
            (
                0,
                0,
                {"name": "Tuesday Morning", "dayofweek": "1", "hour_from": 8, "hour_to": 12, "day_period": "morning"},
            ),
            (
                0,
                0,
                {
                    "name": "Tuesday Afternoon",
                    "dayofweek": "1",
                    "hour_from": 13,
                    "hour_to": 17,
                    "day_period": "afternoon",
                },
            ),
            (
                0,
                0,
                {"name": "Wednesday Morning", "dayofweek": "2", "hour_from": 8, "hour_to": 12, "day_period": "morning"},
            ),
            (
                0,
                0,
                {
                    "name": "Wednesday Afternoon",
                    "dayofweek": "2",
                    "hour_from": 13,
                    "hour_to": 17,
                    "day_period": "afternoon",
                },
            ),
            (
                0,
                0,
                {"name": "Thursday Morning", "dayofweek": "3", "hour_from": 8, "hour_to": 12, "day_period": "morning"},
            ),
            (
                0,
                0,
                {
                    "name": "Thursday Afternoon",
                    "dayofweek": "3",
                    "hour_from": 13,
                    "hour_to": 17,
                    "day_period": "afternoon",
                },
            ),
            (
                0,
                0,
                {"name": "Friday Morning", "dayofweek": "4", "hour_from": 8, "hour_to": 12, "day_period": "morning"},
            ),
            (
                0,
                0,
                {
                    "name": "Friday Afternoon",
                    "dayofweek": "4",
                    "hour_from": 13,
                    "hour_to": 17,
                    "day_period": "afternoon",
                },
            ),
        ]
        company_calendar = self.env["resource.calendar"].create(
            {
                "name": "Full Time Calendar",
                "company_id": company.id,
                "hours_per_day": 8,
                "attendance_ids": company_calendar_attendance_ids,
            }
        )
        company.resource_calendar_id = company_calendar

        part_time_attendance_ids = [
            (
                0,
                0,
                {"name": "Monday Morning", "dayofweek": "0", "hour_from": 8, "hour_to": 12, "day_period": "morning"},
            ),
            (
                0,
                0,
                {
                    "name": "Monday Afternoon",
                    "dayofweek": "0",
                    "hour_from": 13,
                    "hour_to": 17,
                    "day_period": "afternoon",
                },
            ),
            (
                0,
                0,
                {"name": "Tuesday Morning", "dayofweek": "1", "hour_from": 8, "hour_to": 12, "day_period": "morning"},
            ),
            (
                0,
                0,
                {
                    "name": "Tuesday Afternoon",
                    "dayofweek": "1",
                    "hour_from": 13,
                    "hour_to": 17,
                    "day_period": "afternoon",
                },
            ),
            (
                0,
                0,
                {"name": "Wednesday Morning", "dayofweek": "2", "hour_from": 8, "hour_to": 12, "day_period": "morning"},
            ),
            (
                0,
                0,
                {
                    "name": "Wednesday Afternoon",
                    "dayofweek": "2",
                    "hour_from": 13,
                    "hour_to": 17,
                    "day_period": "afternoon",
                },
            ),
        ]
        part_time_calendar = self.env["resource.calendar"].create(
            {
                "name": "Part Time Calendar",
                "company_id": company.id,
                "attendance_ids": part_time_attendance_ids,
            }
        )

        unmatched_part_time_attendance_ids = [
            (
                0,
                0,
                {"name": "Monday Morning", "dayofweek": "0", "hour_from": 9, "hour_to": 13, "day_period": "morning"},
            ),
            (
                0,
                0,
                {
                    "name": "Monday Afternoon",
                    "dayofweek": "0",
                    "hour_from": 14,
                    "hour_to": 18,
                    "day_period": "afternoon",
                },
            ),
            (
                0,
                0,
                {"name": "Tuesday Morning", "dayofweek": "1", "hour_from": 9, "hour_to": 13, "day_period": "morning"},
            ),
            (
                0,
                0,
                {
                    "name": "Tuesday Afternoon",
                    "dayofweek": "1",
                    "hour_from": 14,
                    "hour_to": 18,
                    "day_period": "afternoon",
                },
            ),
            (
                0,
                0,
                {"name": "Wednesday Morning", "dayofweek": "2", "hour_from": 9, "hour_to": 13, "day_period": "morning"},
            ),
            (
                0,
                0,
                {
                    "name": "Wednesday Afternoon",
                    "dayofweek": "2",
                    "hour_from": 14,
                    "hour_to": 18,
                    "day_period": "afternoon",
                },
            ),
        ]
        unmatched_part_time_calendar = self.env["resource.calendar"].create(
            {
                "name": "Unmatched Part Time Calendar",
                "company_id": company.id,
                "attendance_ids": unmatched_part_time_attendance_ids,
            }
        )

        credit_time_work_entry_type = self.env["hr.work.entry.type"].create(
            {
                "name": "Credit Time",
                "code": "CREDIT",
            }
        )

        employees = self.env["hr.employee"].create(
            [
                {
                    "name": "Employee 1",
                    "company_id": company.id,
                    "time_credit": False,
                    "resource_calendar_id": company_calendar.id,
                },
                {
                    "name": "Employee 2",
                    "company_id": company.id,
                    "time_credit": False,
                    "resource_calendar_id": part_time_calendar.id,
                },
                {
                    "name": "Employee 3",
                    "company_id": company.id,
                    "time_credit": True,
                    "resource_calendar_id": part_time_calendar.id,
                    "time_credit_type_id": credit_time_work_entry_type.id,
                },
                {
                    "name": "Employee 4",
                    "company_id": company.id,
                    "time_credit": True,
                    "resource_calendar_id": unmatched_part_time_calendar.id,
                    "time_credit_type_id": credit_time_work_entry_type.id,
                },
            ]
        )
        return {
            "employee_ids": employees.ids,
            "company_calendar_id": company_calendar.id,
            "part_time_calendar_id": part_time_calendar.id,
            "unmatched_part_time_calendar_id": unmatched_part_time_calendar.id,
            "credit_time_work_entry_type_id": credit_time_work_entry_type.id,
        }

    def check(self, init):
        if not init:
            return

        employees = self.env["hr.employee"].browse(init["employee_ids"])
        company_calendar = self.env["resource.calendar"].browse(init["company_calendar_id"])
        part_time_calendar = self.env["resource.calendar"].browse(init["part_time_calendar_id"])
        unmatched_part_time_calendar = self.env["resource.calendar"].browse(init["unmatched_part_time_calendar_id"])
        credit_time_work_entry_type = self.env["hr.work.entry.type"].browse(init["credit_time_work_entry_type_id"])

        credit_time_work_entry_type.l10n_be_is_time_credit = True

        # First employee should not have changed calendar
        self.assertEqual(employees[0].resource_calendar_id, company_calendar)
        # Second employee should not have changed calendar as not credit time
        self.assertEqual(employees[1].resource_calendar_id, part_time_calendar)
        # Third employee should have changed calendar
        self.assertNotEqual(employees[2].resource_calendar_id, part_time_calendar)
        attendances = employees[2].resource_calendar_id.attendance_ids
        attendance_lines = attendances.filtered(lambda a: a.dayofweek in ("0", "1", "2"))
        time_credit_lines = attendances.filtered(lambda a: a.dayofweek in ("3", "4"))
        self.assertFalse(any(attendance_lines.mapped("work_entry_type_id.l10n_be_is_time_credit")))
        self.assertTrue(all(time_credit_lines.mapped("work_entry_type_id.l10n_be_is_time_credit")))
        self.assertEqual(len(time_credit_lines.mapped("work_entry_type_id")), 1)
        self.assertEqual(time_credit_lines.mapped("work_entry_type_id")[0], credit_time_work_entry_type)
        # Fourth employee should not have changed calendar as mismatch
        self.assertEqual(employees[3].resource_calendar_id, unmatched_part_time_calendar)
