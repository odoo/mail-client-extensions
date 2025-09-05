from datetime import date, datetime

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("18.5")
class CheckOvertimeRuleUpgrade(UpgradeCase):
    def prepare(self):
        if not util.version_gte("saas~18.4"):
            self.skipTest("This test is only valid from saas~18.4+")
        company = self.env["res.company"].create(
            {
                "name": "SweatChipChop Inc.",
                "attendance_overtime_validation": "no_validation",
            }
        )
        employee = self.env["hr.employee"].create(
            {
                "name": "Marie-Edouard De La Court",
                "company_id": company.id,
                "tz": "UTC",
                "date_version": date(2020, 1, 1),
                "contract_date_start": date(2020, 1, 1),
                "resource_calendar_id": company.resource_calendar_id.id,
            }
        )

        self.env["hr.attendance"].create(
            {
                "employee_id": employee.id,
                "check_in": datetime(2021, 1, 4, 8, 0),
                "check_out": datetime(2021, 1, 4, 19, 0),
            }
        ).write(
            {
                "overtime_status": "approved",
                "validated_overtime_hours": 5,
            }
        )

        self.env["hr.attendance"].create(
            {
                "employee_id": employee.id,
                "check_in": datetime(2021, 1, 4, 19, 0),
                "check_out": datetime(2021, 1, 4, 20, 0),
            }
        ).write(
            {
                "overtime_status": "refused",
            }
        )
        self.env["hr.attendance"].create(
            {
                "employee_id": employee.id,
                "check_in": datetime(2021, 1, 4, 20, 0),
                "check_out": datetime(2021, 1, 4, 22, 0),
            }
        ).write(
            {
                "overtime_status": "refused",
            }
        )

        return {
            "company_id": company.id,
            "employee_id": employee.id,
        }

    def check(self, init):
        # there should be 2 overtimes for the 4th Jan with 2 different statuses
        # we must have a ruleset with 2 rules
        if not init:
            return

        [ot1, ot2] = self.env["hr.attendance.overtime.line"].search([("employee_id", "=", init["employee_id"])])
        assert ot1.duration == 2.0
        assert ot1.manual_duration == 5.0
        assert ot1.status == "approved"

        assert ot2.duration == 3.0
        assert ot2.status == "refused"
