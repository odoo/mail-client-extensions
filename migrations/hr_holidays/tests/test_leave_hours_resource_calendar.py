from datetime import datetime, timedelta

from freezegun import freeze_time

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("17.0")
class TestLeaveHoursResourceCalendar(UpgradeCase):
    """
    Test to verify that the number_of_hours field on hr.leave records
    is correctly preserved after upgrade when using custom resource calendars.

    This test creates an employee with a custom resource calendar where
    Friday has reduced working hours, then creates a leave spanning from
    Thursday to Tuesday (including the Friday), and verifies that the
    number_of_hours calculation remains correct post-upgrade.
    """

    @freeze_time("2024-01-01")
    def prepare(self):
        # Create a custom resource calendar with different Friday hours
        # Mon-Thu: 8:00-12:30 + 13:00-17:00 (8.5 hours)
        # Friday: 8:00-12:30 + 13:00-14:30 (6 hours)
        resource_calendar = self.env["resource.calendar"].create(
            {
                "name": "Custom Friday Schedule",
                "hours_per_day": 8.0,  # Average hours per day
                "tz": "UTC",
            }
        )

        # Create calendar attendances for Monday to Thursday 8-12:30 and 13-17
        for weekday in [0, 1, 2, 3]:
            self.env["resource.calendar.attendance"].create(
                {
                    "name": "Morning",
                    "dayofweek": str(weekday),
                    "hour_from": 8.0,
                    "hour_to": 12.5,
                    "calendar_id": resource_calendar.id,
                }
            )
            self.env["resource.calendar.attendance"].create(
                {
                    "name": "Afternoon",
                    "dayofweek": str(weekday),
                    "hour_from": 13.0,
                    "hour_to": 17.0,
                    "calendar_id": resource_calendar.id,
                }
            )

        # Friday (reduced hours) 8-12:30 and 13-14:30
        self.env["resource.calendar.attendance"].create(
            {
                "name": "Morning",
                "dayofweek": "4",
                "hour_from": 8.0,
                "hour_to": 12.5,
                "calendar_id": resource_calendar.id,
            }
        )
        self.env["resource.calendar.attendance"].create(
            {
                "name": "Afternoon",
                "dayofweek": "4",
                "hour_from": 13.0,
                "hour_to": 14.5,
                "calendar_id": resource_calendar.id,
            }
        )

        employee = self.env["hr.employee"].create(
            {
                "name": "Test Employee Custom Schedule",
                "resource_calendar_id": resource_calendar.id,
            }
        )

        leave_type = self.env["hr.leave.type"].create(
            {
                "name": "Test Leave Type",
                "time_type": "leave",
                "requires_allocation": "no",
                "employee_requests": "yes",
                "request_unit": "hour",  # Force computation by hours
            }
        )

        # Leave spans from Thursday to Tuesday (4 working days). This will include the Friday with reduced hours
        # Jan 4, 2024 is a Thursday -- Jan 9, 2024 is a Tuesday
        thursday_date = datetime(2024, 1, 4)
        tuesday_date = datetime(2024, 1, 9)

        leave = self.env["hr.leave"].create(
            {
                "name": "Test Leave Thu-Tue",
                "holiday_status_id": leave_type.id,
                "employee_id": employee.id,
                "request_date_from": thursday_date.date(),
                "request_date_to": tuesday_date.date(),
                "date_from": thursday_date,
                "date_to": tuesday_date + timedelta(hours=23, minutes=59, seconds=59),
            }
        )
        leave.action_validate()

        return {
            "leave_id": leave.id,
            "duration": leave.duration_display,
        }

    def check(self, init):
        leave = self.env["hr.leave"].browse(init["leave_id"])
        self.assertEqual(leave.duration_display, init["duration"])
