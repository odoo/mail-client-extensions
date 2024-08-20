import uuid

from odoo import release
from odoo.tools.float_utils import float_round

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


class BRTCommon:
    def _create_employees(self):
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

        ec1 = ec2 = ec3 = {}
        if release.series != "saas~17.4":
            ec1 = {"billing_rate_target": 80}
            ec2 = {"billing_rate_target": 60}
            ec3 = {"billing_rate_target": 40}

        company1, company2, company3 = self.env["res.company"].create(
            [
                {
                    "name": f"Company1 - {uuid.uuid4()}",
                    "resource_calendar_id": resource_calendar_std_38h.id,
                    **ec1,
                },
                {
                    "name": f"Company2 - {uuid.uuid4()}",
                    "resource_calendar_id": resource_calendar_std_35h.id,
                    **ec2,
                },
                {
                    "name": f"Company3 - {uuid.uuid4()}",
                    **ec3,
                },
            ]
        )

        return self.env["hr.employee"].create(
            [
                {
                    "name": f"Employee1 - {uuid.uuid4()}",
                    "company_id": company1.id,
                    "resource_calendar_id": resource_calendar_std_38h.id,
                },
                {
                    "name": f"Employee2 - {uuid.uuid4()}",
                    "company_id": company2.id,
                    "resource_calendar_id": resource_calendar_std_35h.id,
                },
                {
                    "name": f"Employee3 - {uuid.uuid4()}",
                    "company_id": company3.id,
                    "resource_calendar_id": False,
                },
            ]
        )


@change_version("saas~17.4")
class TestMigrateHrEmployeeBillingRateTarget(UpgradeCase, BRTCommon):
    def prepare(self):
        employees = self._create_employees()
        employees[0].billable_time_target = 150.0
        employees[1].billable_time_target = 100.0
        employees[2].billable_time_target = 120.0
        return employees.ids

    def check(self, init):
        if release.series != "saas~17.4":
            self.skipTest("Only targets version saas~17.4")
        employees_ids = init
        (
            employee1,
            employee2,
            employee3,
        ) = self.env["hr.employee"].browse(employees_ids)
        self.assertEqual(
            float_round(employee1.billing_rate_target, precision_digits=2), 0.79
        )  # (150 * (80 / 100.0)) / (7.6 * 20.0)
        self.assertEqual(
            float_round(employee2.billing_rate_target, precision_digits=2), 0.43
        )  # (100 * (60 / 100.0)) / (7 * 20.0)
        self.assertEqual(
            float_round(employee3.billing_rate_target, precision_digits=2), 0.30
        )  # (120 * (40 / 100.0)) / (8 * 20.0)


@change_version("saas~17.5")
class TestMigrateHrEmployeeBillableTimeTarget(UpgradeCase, BRTCommon):
    def prepare(self):
        employees = self._create_employees()
        if release.series == "saas~17.4":
            employees[0].billing_rate_target = 1.0
            employees[1].billing_rate_target = 0.5
            employees[2].billing_rate_target = 0.0
        else:
            employees[0].billable_time_target = 152.0
            employees[1].billable_time_target = 70.0
            employees[2].billable_time_target = 0.0

        return employees.ids

    def check(self, init):
        employees_ids = init
        (
            employee1,
            employee2,
            employee3,
        ) = self.env["hr.employee"].browse(employees_ids)
        self.assertEqual(employee1.billable_time_target, 152.0)  # 1.0 * (20 * 7.6)
        self.assertEqual(employee2.billable_time_target, 70.0)  # 0.5 * (20 * 7)
        self.assertEqual(employee3.billable_time_target, 0.0)  # shouldn't be edited
