# -*- coding: utf-8 -*-

import time

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~14.5")
class TestLinkAllocation(UpgradeCase):
    def prepare(self):
        employees = self.env["hr.employee"].create(
            [
                {
                    "name": "emp_1",
                },
                {
                    "name": "emp_2",
                },
            ]
        )
        leave_type = self.env["hr.leave.type"].create(
            {
                "name": "Paid Time Off - %s" % time.strftime("%Y"),
                "time_type": "leave",
                "allocation_type": "fixed",
                "validity_start": time.strftime("%Y-01-01"),
                "validity_stop": time.strftime("%Y-12-31"),
            }
        )
        allocations = self.env["hr.leave.allocation"].create(
            [
                # Running - good employee
                {
                    "employee_id": employees[0].id,
                    "holiday_status_id": leave_type.id,
                    "number_of_days": 5,
                    "state": "validate",
                },
                # Not running - good employee
                {
                    "employee_id": employees[0].id,
                    "holiday_status_id": leave_type.id,
                    "number_of_days": 10,
                },
                # running - bad employee
                {
                    "employee_id": employees[1].id,
                    "holiday_status_id": leave_type.id,
                    "date_from": time.strftime("%Y-01-01"),
                    "date_to": time.strftime("%Y-12-31"),
                    "number_of_days": 5,
                    "state": "validate",
                },
            ]
        )
        leave = self.env["hr.leave"].create(
            {
                "employee_id": employees[0].id,
                "holiday_status_id": leave_type.id,
                "date_from": time.strftime("%Y-11-15"),
                "date_to": time.strftime("%Y-11-16"),
            }
        )
        leave.state = "confirm"
        leave.action_validate()
        return (
            [emp.id for emp in employees],
            leave_type.id,
            [alloc.id for alloc in allocations],
            leave.id,
        )

    def check(self, init):
        emp_ids, leave_type_id, alloc_ids, leave_id = init

        leave = self.env["hr.leave"].browse(leave_id)
        self.assertEqual(leave.holiday_allocation_id.id, alloc_ids[0])
        employee_days = self.env["hr.leave.type"].browse(leave_type_id).get_employees_days(emp_ids)
        self.assertTrue(employee_days[emp_ids[0]][leave_type_id]["remaining_leaves"] < 5)
        self.assertEqual(employee_days[emp_ids[1]][leave_type_id]["remaining_leaves"], 5)
