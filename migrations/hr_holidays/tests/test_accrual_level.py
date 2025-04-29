import ast
import contextlib
import re

with contextlib.suppress(ImportError):
    from odoo import Command

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.3")
class TestAccrualLevel(UpgradeCase):
    def prepare(self):
        plan = self.env["hr.leave.accrual.plan"].create(
            {
                "name": "Accrual Plan",
                "accrued_gain_time": "start",
                "carryover_date": "other",
                "carryover_day": 20,
                "carryover_month": "apr",
                "level_ids": [
                    Command.create(
                        {
                            "added_value": 8,
                            "added_value_type": "day",
                            "action_with_unused_accruals": "lost",
                            "frequency": "bimonthly",
                            "first_day": 3,
                            "second_day": 20,
                        }
                    ),
                    Command.create(
                        {
                            "added_value": 2,
                            "added_value_type": "day",
                            "action_with_unused_accruals": "lost",
                            "frequency": "monthly",
                            "first_day_display": "last",
                        }
                    ),
                    Command.create(
                        {
                            "added_value": 3,
                            "added_value_type": "day",
                            "action_with_unused_accruals": "lost",
                            "frequency": "biyearly",
                            "first_month": "jan",
                            "first_month_day": 15,
                            "second_month": "jul",
                            "second_month_day_display": "last",
                        }
                    ),
                ],
            }
        )

        search_view = self.env["ir.ui.view"].create(
            {
                "name": "hr.leave.accrual.level.search",
                "type": "search",
                "model": "hr.leave.accrual.level",
                "arch": """
                        <search>
                            <filter name="first_month_day_1" domain="[('first_month_day', '=', 15)]"/>
                            <filter name="first_day_1" domain="[('first_day', '!=', 14)]"/>
                            <filter name="second_day_1" domain="[('second_day', 'in', [12, 13, 14, 15])]"/>
                            <filter name="second_day_2" domain="[('second_day', '>=', 15)]"/>
                            <filter name="first_month" domain="[('second_month', '=', 'jul')]"/>
                        </search>
                    """,
            }
        )

        level_last = self.env["hr.leave.accrual.level"].search([("first_day", "=", 31)])

        return plan.level_ids.ids, search_view.id, level_last.id

    def check(self, init):
        level_ids, search_view_id, level_last_id = init
        level_bimonthly, level_monthly, level_biyearly = self.env["hr.leave.accrual.level"].browse(level_ids)
        view = self.env["ir.ui.view"].browse(search_view_id)

        self.assertEqual(level_bimonthly.first_day, "3")
        self.assertEqual(level_bimonthly.second_day, "20")
        self.assertEqual(level_monthly.first_day, "31")
        self.assertEqual(level_biyearly.first_month, "1")
        self.assertEqual(level_biyearly.second_month, "7")
        self.assertEqual(level_biyearly.first_month_day, "15")
        self.assertEqual(level_biyearly.second_month_day, "31")

        level_last = self.env["hr.leave.accrual.level"].search([("first_day", "=", "31")])
        self.assertEqual(level_last.id, level_last_id)

        domains_regex = re.compile(r"domain=\"(.*?)\"")
        level_search_view_domains = domains_regex.findall(view.arch)
        expected_level_search_view_domains = [
            [("first_month_day", "=", "15")],
            [("first_day", "!=", "14")],
            [("second_day", "in", ["12", "13", "14", "15"])],
            [("second_day", "&gt;=", "15")],
            [("second_month", "=", "7")],
        ]

        for domain_str, expected_domain in zip(level_search_view_domains, expected_level_search_view_domains):
            domain = ast.literal_eval(domain_str)
            self.assertEqual(domain, expected_domain)
