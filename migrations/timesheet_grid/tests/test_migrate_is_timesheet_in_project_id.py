import ast
import re

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.5")
class TestMigrateIsTimesheetToProjectId(UpgradeCase):
    def prepare(self):
        search_view = self.env["ir.ui.view"].create(
            {
                "name": "account.analytic.line.search",
                "type": "search",
                "model": "account.analytic.line",
                "arch": """
                    <search>
                        <filter name="is_timesheet" string="Is Timesheet" domain="[('is_timesheet', '=', True)]"/>
                        <filter name="is_timesheet" string="Is Timesheet 2" domain="[('is_timesheet', '!=', False)]"/>
                        <filter name="is_not_timesheet" string="Is Not Timesheet" domain="[('is_timesheet', '!=', True)]"/>
                        <filter name="is_not_timesheet" string="Is Not Timesheet 2" domain="[('is_timesheet', '=', False)]"/>
                    </search>
                """,
            }
        )
        return search_view.id

    def check(self, init):
        search_view_id = init
        timesheet_search_view = self.env["ir.ui.view"].browse(search_view_id)
        # Check if the domains are correctly adapted
        # Regex to get domain attribute of each filter
        domains_regex = re.compile(r"domain=\"(.*?)\"")
        timesheet_search_view_domains = domains_regex.findall(timesheet_search_view.arch)
        expected_timesheet_search_view_domains = [
            [("project_id", "!=", False)],
            [("project_id", "!=", False)],
            [("project_id", "=", False)],
            [("project_id", "=", False)],
        ]
        for domain_str, expected_domain in zip(timesheet_search_view_domains, expected_timesheet_search_view_domains):
            domain = ast.literal_eval(domain_str)
            left, op, right = domain[0]
            expected_left, expected_op, expected_right = expected_domain[0]
            self.assertEqual(left, expected_left)
            self.assertEqual(op, expected_op)
            self.assertEqual(right, expected_right)
