from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.4")
class TestMigrateHrEmployeeBillingRateTarget(UpgradeCase):
    def prepare(self):
        resource_calendar_std_38h, resource_calendar_std_35h = self.env["resource.calendar"].create(
            [
                {
                    "name": "Standard 38 hours/week",
                    "tz": "Europe/Brussels",
                    "hours_per_day": 7.6,
                    "attendance_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "Monday Morning",
                                "dayofweek": "0",
                                "hour_from": 8,
                                "hour_to": 12,
                                "day_period": "morning",
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": "Monday Lunch",
                                "dayofweek": "0",
                                "hour_from": 12,
                                "hour_to": 13,
                                "day_period": "lunch",
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": "Monday Afternoon",
                                "dayofweek": "0",
                                "hour_from": 13,
                                "hour_to": 16.6,
                                "day_period": "afternoon",
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": "Tuesday Morning",
                                "dayofweek": "1",
                                "hour_from": 8,
                                "hour_to": 12,
                                "day_period": "morning",
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": "Tuesday Lunch",
                                "dayofweek": "1",
                                "hour_from": 12,
                                "hour_to": 13,
                                "day_period": "lunch",
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": "Tuesday Afternoon",
                                "dayofweek": "1",
                                "hour_from": 13,
                                "hour_to": 16.6,
                                "day_period": "afternoon",
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": "Wednesday Morning",
                                "dayofweek": "2",
                                "hour_from": 8,
                                "hour_to": 12,
                                "day_period": "morning",
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": "Wednesday Lunch",
                                "dayofweek": "2",
                                "hour_from": 12,
                                "hour_to": 13,
                                "day_period": "lunch",
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": "Wednesday Afternoon",
                                "dayofweek": "2",
                                "hour_from": 13,
                                "hour_to": 16.6,
                                "day_period": "afternoon",
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": "Thursday Morning",
                                "dayofweek": "3",
                                "hour_from": 8,
                                "hour_to": 12,
                                "day_period": "morning",
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": "Thursday Lunch",
                                "dayofweek": "3",
                                "hour_from": 12,
                                "hour_to": 13,
                                "day_period": "lunch",
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": "Thursday Afternoon",
                                "dayofweek": "3",
                                "hour_from": 13,
                                "hour_to": 16.6,
                                "day_period": "afternoon",
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": "Friday Morning",
                                "dayofweek": "4",
                                "hour_from": 8,
                                "hour_to": 12,
                                "day_period": "morning",
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": "Friday Lunch",
                                "dayofweek": "4",
                                "hour_from": 12,
                                "hour_to": 13,
                                "day_period": "lunch",
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": "Friday Afternoon",
                                "dayofweek": "4",
                                "hour_from": 13,
                                "hour_to": 16.6,
                                "day_period": "afternoon",
                            },
                        ),
                    ],
                },
                {
                    "name": "Standard 35 hours/week",
                    "tz": "Europe/Brussels",
                    "hours_per_day": 7,
                    "attendance_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "Monday Morning",
                                "dayofweek": "0",
                                "hour_from": 8,
                                "hour_to": 12,
                                "day_period": "morning",
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": "Monday Lunch",
                                "dayofweek": "0",
                                "hour_from": 12,
                                "hour_to": 13,
                                "day_period": "lunch",
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": "Monday Evening",
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
                                "hour_from": 8,
                                "hour_to": 12,
                                "day_period": "morning",
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": "Tuesday Lunch",
                                "dayofweek": "1",
                                "hour_from": 12,
                                "hour_to": 13,
                                "day_period": "lunch",
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": "Tuesday Evening",
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
                                "hour_from": 8,
                                "hour_to": 12,
                                "day_period": "morning",
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": "Wednesday Lunch",
                                "dayofweek": "2",
                                "hour_from": 12,
                                "hour_to": 13,
                                "day_period": "lunch",
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": "Wednesday Evening",
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
                                "hour_from": 8,
                                "hour_to": 12,
                                "day_period": "morning",
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": "Thursday Lunch",
                                "dayofweek": "3",
                                "hour_from": 12,
                                "hour_to": 13,
                                "day_period": "lunch",
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": "Thursday Evening",
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
                                "hour_from": 8,
                                "hour_to": 12,
                                "day_period": "morning",
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": "Friday Lunch",
                                "dayofweek": "4",
                                "hour_from": 12,
                                "hour_to": 13,
                                "day_period": "lunch",
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": "Friday Evening",
                                "dayofweek": "4",
                                "hour_from": 13,
                                "hour_to": 16,
                                "day_period": "afternoon",
                            },
                        ),
                    ],
                },
            ]
        )
        company1, company2, company3 = self.env["res.company"].create(
            [
                {
                    "name": "Company1",
                    "resource_calendar_id": resource_calendar_std_38h.id,
                    "billing_rate_target": 80,
                },
                {
                    "name": "Company2",
                    "resource_calendar_id": resource_calendar_std_35h.id,
                    "billing_rate_target": 60,
                },
                {
                    "name": "Company3",
                    "billing_rate_target": 40,
                },
            ]
        )
        employees = self.env["hr.employee"].create(
            [
                {
                    "name": "Employee1",
                    "company_id": company1.id,
                    "billable_time_target": 150,
                },
                {
                    "name": "Employee2",
                    "company_id": company2.id,
                    "billable_time_target": 100,
                },
                {
                    "name": "Employee3",
                    "company_id": company3.id,
                    "billable_time_target": 120,
                },
            ]
        )
        return employees.ids

    def check(self, init):
        employees_ids = init
        (
            employee1,
            employee2,
            employee3,
        ) = self.env["hr.employee"].browse(employees_ids)
        self.assertEqual(round(employee1.billing_rate_target, 2), 0.79)  # (150 * (80 / 100.0)) / (7.6 * 20.0)
        self.assertEqual(round(employee2.billing_rate_target, 2), 0.43)  # (100 * (60 / 100.0)) / (7 * 20.0)
        self.assertEqual(round(employee3.billing_rate_target, 2), 0.30)  # (120 * (40 / 100.0)) / (8 * 20.0)
