from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.5")
class TestFullTimeRequiredHours(UpgradeCase):
    def prepare(self):
        """
        create working calendar without the field full_time_required_hours
        """
        self.new_calendars = (
            self.env["resource.calendar"]
            .with_company(self.env.company)
            .create(
                {
                    "name": "test regular 40h/week",
                    "hours_per_day": 8.0,
                    "attendance_ids": [
                        (0, 0, {"name": "Monday Morning", "dayofweek": "0", "hour_from": 8, "hour_to": 12, "day_period": "morning"}),
                        (0, 0, {"name": "Monday Lunch", "dayofweek": "0", "hour_from": 12, "hour_to": 13, "day_period": "lunch"}),
                        (0, 0, {"name": "Monday Evening", "dayofweek": "0", "hour_from": 13, "hour_to": 17, "day_period": "afternoon"}),
                        (0, 0, {"name": "Tuesday Morning", "dayofweek": "1", "hour_from": 8, "hour_to": 12, "day_period": "morning"}),
                        (0, 0, {"name": "Tuesday Lunch", "dayofweek": "1", "hour_from": 12, "hour_to": 13, "day_period": "lunch"}),
                        (0, 0, {"name": "Tuesday Evening", "dayofweek": "1", "hour_from": 13, "hour_to": 17, "day_period": "afternoon"}),
                        (0, 0, {"name": "Wednesday Morning", "dayofweek": "2", "hour_from": 8, "hour_to": 12, "day_period": "morning"}),
                        (0, 0, {"name": "Wednesday Lunch", "dayofweek": "2", "hour_from": 12, "hour_to": 13, "day_period": "lunch"}),
                        (0, 0, {"name": "Wednesday Evening", "dayofweek": "2", "hour_from": 13, "hour_to": 17, "day_period": "afternoon"}),
                        (0, 0, {"name": "Thursday Morning", "dayofweek": "3", "hour_from": 8, "hour_to": 12, "day_period": "morning"}),
                        (0, 0, {"name": "Thursday Lunch", "dayofweek": "3", "hour_from": 12, "hour_to": 13, "day_period": "lunch"}),
                        (0, 0, {"name": "Thursday Evening", "dayofweek": "3", "hour_from": 13, "hour_to": 17, "day_period": "afternoon"}),
                        (0, 0, {"name": "Friday Morning", "dayofweek": "4", "hour_from": 8, "hour_to": 12, "day_period": "morning"}),
                        (0, 0, {"name": "Friday Lunch", "dayofweek": "4", "hour_from": 12, "hour_to": 13, "day_period": "lunch"}),
                        (0, 0, {"name": "Friday Evening", "dayofweek": "4", "hour_from": 13, "hour_to": 17, "day_period": "afternoon"}),
                    ],
                }
            )
        )
        return {
            "new_calendar_id": self.new_calendars.id,
        }

    def check(self, init):
        """
        check that:
        - new_calendar created in prerate has the field full_time_required_hours and value is set to 40.0
        """
        self.assertEqual(self.env["resource.calendar"].browse(init["new_calendar_id"]).full_time_required_hours, 40.0)
