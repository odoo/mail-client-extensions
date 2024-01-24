# -*- coding: utf-8 -*-

import time

from freezegun import freeze_time

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~14.5")
class TestLinkAllocation(UpgradeCase):
    @freeze_time("2022-12-12")
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
        leave_types = self.env["hr.leave.type"].create(
            [
                {
                    "name": "Paid Time Off - %s" % time.strftime("%Y"),
                    "time_type": "leave",
                    "allocation_type": "fixed",
                    "validity_start": time.strftime("%Y-01-01"),
                    "validity_stop": time.strftime("%Y-12-31"),
                },
                {
                    "name": "Sick Time Off",
                    "time_type": "leave",
                    "leave_validation_type": "no_validation",
                    "allocation_type": "no",
                },
            ]
        )
        allocations = self.env["hr.leave.allocation"].create(
            [
                # Running - good employee
                {
                    "employee_id": employees[0].id,
                    "holiday_status_id": leave_types[0].id,
                    "number_of_days": 5,
                    "state": "validate",
                },
                # Not running - good employee
                {
                    "employee_id": employees[0].id,
                    "holiday_status_id": leave_types[0].id,
                    "number_of_days": 10,
                },
                # running - bad employee
                {
                    "employee_id": employees[1].id,
                    "holiday_status_id": leave_types[0].id,
                    "date_from": time.strftime("%Y-01-01"),
                    "date_to": time.strftime("%Y-12-31"),
                    "number_of_days": 5,
                    "state": "validate",
                },
            ]
        )
        leaves = self.env["hr.leave"].create(
            [
                {
                    "employee_id": employees[0].id,
                    "holiday_status_id": leave_types[0].id,
                    "date_from": time.strftime("%Y-11-15"),
                    "date_to": time.strftime("%Y-11-16"),
                },
                {
                    "employee_id": employees[0].id,
                    "holiday_status_id": leave_types[1].id,
                    "date_from": time.strftime("%Y-12-15"),
                    "date_to": time.strftime("%Y-12-16"),
                },
            ]
        )
        leaves.state = "confirm"
        leaves.action_validate()
        # Change the allocation to a fixed type after creating a leave for it, no allocation exists.
        # This is considered an invalid operation but has to be handled either way.
        leave_types[1].allocation_type = "fixed"
        return (
            [emp.id for emp in employees],
            [leave_type.id for leave_type in leave_types],
            [alloc.id for alloc in allocations],
            [leave.id for leave in leaves],
        )

    @freeze_time("2022-12-12")
    def check(self, init):
        emp_ids, leave_type_ids, alloc_ids, leave_ids = init

        leave = self.env["hr.leave"].browse(leave_ids[0])
        self.assertEqual(leave.holiday_allocation_id.id, alloc_ids[0])
        employee_days = self.env["hr.leave.type"].browse(leave_type_ids[0]).get_employees_days(emp_ids)
        self.assertTrue(employee_days[emp_ids[0]][leave_type_ids[0]]["remaining_leaves"] < 5)
        self.assertEqual(employee_days[emp_ids[1]][leave_type_ids[0]]["remaining_leaves"], 5)

        leave = self.env["hr.leave"].browse(leave_ids[1])
        self.assertTrue(leave.holiday_allocation_id)
