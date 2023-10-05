from datetime import datetime

from odoo.tests import new_test_user

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.5")
class TestMigrateAttendance(UpgradeCase):
    def prepare(self):
        company = self.env["res.company"].create(
            {
                "name": "SweatChipChop Inc.",
                "hr_attendance_overtime": True,
                "overtime_start_date": datetime(2021, 1, 1),
                "overtime_company_threshold": 10,
                "overtime_employee_threshold": 10,
            }
        )
        calendar_attendance_ids = [
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
        employee_calendar = self.env["resource.calendar"].create(
            [
                {
                    "name": "Test Calendar",
                    "company_id": company.id,
                    "hours_per_day": 8,
                    "attendance_ids": calendar_attendance_ids,
                }
            ]
        )

        user = new_test_user(
            self.env,
            login="testupgrade",
            groups="base.group_user,hr_attendance.group_hr_attendance_manager",
            company_id=company.id,
        ).with_company(company)
        employee = self.env["hr.employee"].create(
            {
                "name": "Joshua",
                "user_id": user.id,
                "company_id": company.id,
                "resource_calendar_id": employee_calendar.id,
                "tz": "UTC",
            },
        )
        create_vals = [
            {
                "employee_id": employee.id,
                "check_in": datetime(2023, 1, 2, 8, 0),
                "check_out": datetime(2023, 1, 2, 21, 0),
            },
            {
                "employee_id": employee.id,
                "check_in": datetime(2023, 1, 3, 8, 0),
                "check_out": datetime(2023, 1, 3, 19, 0),
            },
            {
                "employee_id": employee.id,
                "check_in": datetime(2023, 1, 3, 19, 0),
                "check_out": datetime(2023, 1, 3, 20, 0),
            },
            {
                "employee_id": employee.id,
                "check_in": datetime(2023, 1, 3, 21, 0),
                "check_out": datetime(2023, 1, 3, 23, 0),
            },
            {
                "employee_id": employee.id,
                "check_in": datetime(2023, 1, 5, 10, 0),
                "check_out": datetime(2023, 1, 5, 14, 0),
            },
            {
                "employee_id": employee.id,
                "check_in": datetime(2023, 1, 5, 15, 0),
                "check_out": datetime(2023, 1, 5, 16, 0),
            },
        ]

        created_ids = []

        for val in create_vals:
            new_attendance = self.env["hr.attendance"].create(val)
            created_ids.append(new_attendance.id)

        return {"ids": created_ids}

    def check(self, init):
        attendances_overtimes = self.env["hr.attendance"].browse(init["ids"]).mapped("overtime_hours")
        expected_overtime_hours = [5, 3, 1, 2, 0, 0]
        for i in range(len(attendances_overtimes)):
            self.assertAlmostEqual(attendances_overtimes[i], expected_overtime_hours[i], 2)
