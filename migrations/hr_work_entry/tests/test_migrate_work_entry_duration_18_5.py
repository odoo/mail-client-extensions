from datetime import datetime

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.5")
class TestMigrateWorkEntry(UpgradeCase):
    def prepare(self):
        if not util.table_exists(self.env.cr, "hr_version"):
            self.skipTest("Skip test as hr.version doesn't exist here")

        # create resource calendars with different timezone configurations
        calendar_brussels = self.env["resource.calendar"].create(
            {
                "name": "Brussels",
                "tz": "Europe/Brussels",
                "attendance_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Monday Morning",
                            "dayofweek": "0",
                            "hour_from": 7,
                            "hour_to": 12,
                            "day_period": "morning",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Monday Afternoon",
                            "dayofweek": "0",
                            "hour_from": 13,
                            "hour_to": 16,
                            "day_period": "afternoon",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Tuesday Morning",
                            "dayofweek": "1",
                            "hour_from": 7,
                            "hour_to": 12,
                            "day_period": "morning",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Tuesday Afternoon",
                            "dayofweek": "1",
                            "hour_from": 13,
                            "hour_to": 16,
                            "day_period": "afternoon",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Wednesday Morning",
                            "dayofweek": "2",
                            "hour_from": 7,
                            "hour_to": 12,
                            "day_period": "morning",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Wednesday Afternoon",
                            "dayofweek": "2",
                            "hour_from": 13,
                            "hour_to": 16,
                            "day_period": "afternoon",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Thursday Morning",
                            "dayofweek": "3",
                            "hour_from": 7,
                            "hour_to": 12,
                            "day_period": "morning",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Thursday Afternoon",
                            "dayofweek": "3",
                            "hour_from": 13,
                            "hour_to": 16,
                            "day_period": "afternoon",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Friday Morning",
                            "dayofweek": "4",
                            "hour_from": 7,
                            "hour_to": 12,
                            "day_period": "morning",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Friday Afternoon",
                            "dayofweek": "4",
                            "hour_from": 13,
                            "hour_to": 16,
                            "day_period": "afternoon",
                        },
                    ),
                ],
            }
        )

        calendar_utc = self.env["resource.calendar"].create(
            {
                "name": "UTC",
                "tz": "UTC",
                "attendance_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Monday Morning",
                            "dayofweek": "0",
                            "hour_from": 7,
                            "hour_to": 12,
                            "day_period": "morning",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Monday Afternoon",
                            "dayofweek": "0",
                            "hour_from": 13,
                            "hour_to": 16,
                            "day_period": "afternoon",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Tuesday Morning",
                            "dayofweek": "1",
                            "hour_from": 7,
                            "hour_to": 12,
                            "day_period": "morning",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Tuesday Afternoon",
                            "dayofweek": "1",
                            "hour_from": 13,
                            "hour_to": 16,
                            "day_period": "afternoon",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Wednesday Morning",
                            "dayofweek": "2",
                            "hour_from": 7,
                            "hour_to": 12,
                            "day_period": "morning",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Wednesday Afternoon",
                            "dayofweek": "2",
                            "hour_from": 13,
                            "hour_to": 16,
                            "day_period": "afternoon",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Thursday Morning",
                            "dayofweek": "3",
                            "hour_from": 7,
                            "hour_to": 12,
                            "day_period": "morning",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Thursday Afternoon",
                            "dayofweek": "3",
                            "hour_from": 13,
                            "hour_to": 16,
                            "day_period": "afternoon",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Friday Morning",
                            "dayofweek": "4",
                            "hour_from": 7,
                            "hour_to": 12,
                            "day_period": "morning",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Friday Afternoon",
                            "dayofweek": "4",
                            "hour_from": 13,
                            "hour_to": 16,
                            "day_period": "afternoon",
                        },
                    ),
                ],
            }
        )

        company = self.env["res.company"].create(
            {
                "name": "Test Company",
                "resource_calendar_id": calendar_utc.id,
            }
        )

        employee1 = self.env["hr.employee"].create(
            {
                "name": "Employee 1",
                "company_id": company.id,
            }
        )
        employee2 = self.env["hr.employee"].create(
            {
                "name": "Employee 2",
                "company_id": company.id,
            }
        )

        # create version with different calendars
        contract1 = self.env["hr.version"].create(
            {
                "name": "Contract 1",
                "employee_id": employee1.id,
                "resource_calendar_id": calendar_brussels.id,
                "company_id": company.id,
                "date_version": "2023-01-01",
                "contract_date_start": "2023-01-01",
                "wage": 1000,
            }
        )

        contract2 = self.env["hr.version"].create(
            {
                "name": "Contract 2",
                "employee_id": employee2.id,
                "resource_calendar_id": calendar_utc.id,
                "company_id": company.id,
                "date_version": "2023-01-01",
                "contract_date_start": "2023-01-01",
                "wage": 1000,
            }
        )

        # Create work entry types
        work_entry_type_attendance = self.env["hr.work.entry.type"].create(
            {
                "name": "Attendance",
                "code": "ATTENDANCE",
            }
        )
        work_entry_type_leave = self.env["hr.work.entry.type"].create(
            {
                "name": "Leave",
                "code": "LEAVE",
            }
        )

        # 1. Single-day entry
        self.env["hr.work.entry"].create(
            {
                "name": "Work entry 2",
                "employee_id": employee1.id,
                "version_id": contract1.id,
                "work_entry_type_id": work_entry_type_attendance.id,
                "date_start": datetime(2023, 1, 3, 8, 0),
                "date_stop": datetime(2023, 1, 3, 12, 0),
                "duration": 4,
            }
        )

        # 2. Entry with pre-set date
        self.env["hr.work.entry"].create(
            {
                "name": "Work entry 4",
                "employee_id": employee1.id,
                "version_id": contract1.id,
                "work_entry_type_id": work_entry_type_attendance.id,
                "date_start": datetime(2023, 1, 6, 8, 0),
                "date_stop": datetime(2023, 1, 6, 10, 0),
                "duration": 2,
            }
        )

        # 3 & 4. Entries to be merged (same day, same type)
        self.env["hr.work.entry"].create(
            {
                "name": "Work entry 5",
                "employee_id": employee1.id,
                "version_id": contract1.id,
                "work_entry_type_id": work_entry_type_attendance.id,
                "date_start": datetime(2023, 1, 7, 8, 0),
                "date_stop": datetime(2023, 1, 7, 10, 0),
                "duration": 2,
            }
        )
        self.env["hr.work.entry"].create(
            {
                "name": "Work entry 6",
                "employee_id": employee1.id,
                "version_id": contract1.id,
                "work_entry_type_id": work_entry_type_attendance.id,
                "date_start": datetime(2023, 1, 7, 14, 0),
                "date_stop": datetime(2023, 1, 7, 16, 0),
                "duration": 2,
            }
        )

        # 5. Entry on same day but different type (should not merge)
        self.env["hr.work.entry"].create(
            {
                "name": "Work entry 7",
                "employee_id": employee1.id,
                "version_id": contract1.id,
                "work_entry_type_id": work_entry_type_leave.id,
                "date_start": datetime(2023, 1, 7, 10, 0),
                "date_stop": datetime(2023, 1, 7, 12, 0),
                "duration": 2,
            }
        )

        return {
            "employee1_id": employee1.id,
            "employee2_id": employee2.id,
            "contract1_id": contract1.id,
            "contract2_id": contract2.id,
            "work_entry_type_attendance_id": work_entry_type_attendance.id,
            "work_entry_type_leave_id": work_entry_type_leave.id,
        }

    def check(self, init):
        # Verify work_entry2: Remains single entry
        entry1 = self.env["hr.work.entry"].search(
            [
                ("employee_id", "=", init["employee1_id"]),
                ("version_id", "=", init["contract1_id"]),
                ("work_entry_type_id", "=", init["work_entry_type_attendance_id"]),
                ("date", "=", "2023-01-03"),
            ]
        )
        self.assertEqual(len(entry1), 1, "Single-day entry should not be split.")
        self.assertEqual(entry1.duration, 4, "Duration should remain 4 hours.")
        self.assertEqual(
            entry1.date,
            datetime(2023, 1, 3).date(),
            "Date should be set to 2023-01-03.",
        )

        # Verify work_entry2: Date preserved or set correctly
        entry2 = self.env["hr.work.entry"].search(
            [
                ("employee_id", "=", init["employee1_id"]),
                ("version_id", "=", init["contract1_id"]),
                ("work_entry_type_id", "=", init["work_entry_type_attendance_id"]),
                ("date", "=", "2023-01-06"),
            ]
        )
        self.assertEqual(len(entry2), 1, "Entry with pre-set date should remain single.")
        self.assertEqual(entry2.duration, 2, "Duration should remain 2 hours.")
        self.assertEqual(entry2.date, datetime(2023, 1, 6).date(), "Date should be 2023-01-06.")

        # Verify work_entry3 & 4: Merged into one entry
        merged_entry = self.env["hr.work.entry"].search(
            [
                ("employee_id", "=", init["employee1_id"]),
                ("version_id", "=", init["contract1_id"]),
                ("work_entry_type_id", "=", init["work_entry_type_attendance_id"]),
                ("date", "=", "2023-01-07"),
            ]
        )
        self.assertEqual(len(merged_entry), 1, "Similar entries on 2023-01-07 should be merged.")
        self.assertEqual(merged_entry.duration, 4, "Merged duration should be 4 hours.")

        # Verify work_entry7: Not merged due to different type
        entry5 = self.env["hr.work.entry"].search(
            [
                ("employee_id", "=", init["employee1_id"]),
                ("version_id", "=", init["contract1_id"]),
                ("work_entry_type_id", "=", init["work_entry_type_leave_id"]),
                ("date", "=", "2023-01-07"),
            ]
        )
        self.assertEqual(len(entry5), 1, "Entry with different type should not be merged.")
        self.assertEqual(entry5.duration, 2, "Duration should remain 2 hours.")
