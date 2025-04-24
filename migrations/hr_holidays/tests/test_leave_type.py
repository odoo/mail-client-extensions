import ast
import re

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.3")
class TestAccrualLevel(UpgradeCase):
    def prepare(self):
        leave_types = self.env["hr.leave.type"].create(
            [
                {
                    "name": "with validation and allocation request",
                    "time_type": "leave",
                    "requires_allocation": "yes",
                    "employee_requests": "yes",
                },
                {
                    "name": "without validation and allocation request",
                    "requires_allocation": "no",
                    "employee_requests": "no",
                },
            ]
        )

        search_view = self.env["ir.ui.view"].create(
            {
                "name": "hr.leave.type.search",
                "type": "search",
                "model": "hr.leave.type",
                "arch": """
                        <search>
                            <filter name="requires_allocation" domain="[('requires_allocation', '=', 'yes')]"/>
                            <filter name="employee_requests" domain="[('employee_requests', '!=', 'no')]"/>
                            <filter name="second_day_1" domain="[('employee_requests', 'in', ['yes', 'no'])]"/>
                        </search>
                    """,
            }
        )

        leave_type_without_requires_allocation = self.env["hr.leave.type"].search(
            [
                ("requires_allocation", "=", "no"),
                ("name", "=", "without validation and allocation request"),
            ]
        )

        return leave_types.ids, search_view.id, leave_type_without_requires_allocation.id

    def check(self, init):
        leave_types_ids, search_view_id, leave_type_without_requires_allocation_id = init
        leave_type_with, leave_type_without = self.env["hr.leave.type"].browse(leave_types_ids)
        view = self.env["ir.ui.view"].browse(search_view_id)

        self.assertTrue(leave_type_with.requires_allocation)
        self.assertFalse(leave_type_without.requires_allocation)
        self.assertTrue(leave_type_with.employee_requests)
        self.assertFalse(leave_type_without.employee_requests)

        leave_type_without_requires_allocation = self.env["hr.leave.type"].search(
            [
                ("requires_allocation", "=", False),
                ("name", "=", "without validation and allocation request"),
            ]
        )
        self.assertEqual(leave_type_without_requires_allocation.id, leave_type_without_requires_allocation_id)

        domains_regex = re.compile(r"domain=\"(.*?)\"")
        leave_type_search_view_domains = domains_regex.findall(view.arch)
        expected_leave_type_search_view_domains = [
            [("requires_allocation", "=", True)],
            [("employee_requests", "!=", False)],
            [("employee_requests", "in", [True, False])],
        ]

        for domain_str, expected_domain in zip(leave_type_search_view_domains, expected_leave_type_search_view_domains):
            domain = ast.literal_eval(domain_str)
            self.assertEqual(domain, expected_domain)
