from datetime import datetime

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.5")
class TestMigrateAttendance(UpgradeCase):
    def prepare(self):
        no_overtime_company = self.env["res.company"].create(
            {
                "name": "SweatChipChop No OT Inc.",
                "hr_attendance_overtime": False,
            }
        )

        overtime_company = self.env["res.company"].create(
            {
                "name": "SweatChipChop OT Inc.",
                "hr_attendance_overtime": True,
                "overtime_start_date": datetime(2021, 1, 1),
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
                    "company_id": no_overtime_company.id,
                    "hours_per_day": 8,
                    "attendance_ids": calendar_attendance_ids,
                }
            ]
        )

        employee_calendar_2 = self.env["resource.calendar"].create(
            [
                {
                    "name": "Test Calendar 2",
                    "company_id": overtime_company.id,
                    "hours_per_day": 8,
                    "attendance_ids": calendar_attendance_ids,
                }
            ]
        )

        employee = self.env["hr.employee"].create(
            {
                "name": "Joshua",
                "company_id": no_overtime_company.id,
                "resource_calendar_id": employee_calendar.id,
                "tz": "UTC",
            },
        )

        employee2 = self.env["hr.employee"].create(
            {
                "name": "Joshua OT",
                "company_id": overtime_company.id,
                "resource_calendar_id": employee_calendar_2.id,
                "tz": "UTC",
            },
        )

        attendances = self.env["hr.attendance"].create(
            [
                {  # No overtime company attendance
                    "employee_id": employee.id,
                    "check_in": datetime(2020, 1, 2, 8, 0),
                    "check_out": datetime(2020, 1, 2, 21, 0),
                },
                {  # Pre-overtime enabled attendance
                    "employee_id": employee2.id,
                    "check_in": datetime(2020, 1, 2, 8, 0),
                    "check_out": datetime(2020, 1, 2, 21, 0),
                },
                {  # Post-overtime enabled attendance
                    "employee_id": employee2.id,
                    "check_in": datetime(2023, 1, 3, 8, 0),
                    "check_out": datetime(2023, 1, 3, 19, 0),
                },
            ]
        )

        return {
            "attendance_ids": attendances.ids,
            "overtime_company_id": overtime_company.id,
            "no_overtime_company": no_overtime_company.id,
        }

    def check(self, init):
        attendances = self.env["hr.attendance"].browse(init["attendance_ids"])
        ot_company = self.env["res.company"].browse(init["overtime_company_id"])
        no_ot_company = self.env["res.company"].browse(init["no_overtime_company"])

        self.assertEqual(ot_company.attendance_overtime_validation, "no_validation")
        self.assertEqual(no_ot_company.attendance_overtime_validation, "by_manager")

        self.assertEqual(attendances[0].overtime_status, "refused")
        self.assertEqual(attendances[1].overtime_status, "refused")
        self.assertEqual(attendances[2].overtime_status, "approved")

        self.assertAlmostEqual(attendances[0].validated_overtime_hours, 0, 2)
        self.assertAlmostEqual(attendances[1].validated_overtime_hours, 0, 2)
        self.assertAlmostEqual(attendances[2].validated_overtime_hours, 3, 2)

        self.assertAlmostEqual(attendances[0].employee_id.total_overtime, 0, 2)
        self.assertAlmostEqual(attendances[2].employee_id.total_overtime, 3, 2)
