# -*- coding: utf-8 -*-
import contextlib

with contextlib.suppress(ImportError):
    from odoo import Command

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("16.0")
class TestLinePlanIdSyncIfGroupless(UpgradeCase):
    def prepare(self):
        # Creating an account without field group set. this field was 'renamed' to plan in 16
        analytic_account = self.env["account.analytic.account"].create(
            {
                "name": "Test Analytic Account",
                "line_ids": [
                    # Creating an analytic line related to this account, it should not have a group to it
                    Command.create({"name": "Test Analytic Line"})
                ],
            }
        )

        assert not analytic_account.line_ids[0].group_id

        return analytic_account.id

    def check(self, analytic_account_id):
        analytic_account = self.env["account.analytic.account"].browse(analytic_account_id)

        default_upg_plan = self.env["account.analytic.plan"].search([("name", "=", "Default upg")], limit=1)

        # After upgrade, both account and line should have plan_id pointing to the newly created 'Default upg' plan
        self.assertEqual(analytic_account.plan_id.id, default_upg_plan.id)
        self.assertEqual(analytic_account.line_ids[0].plan_id.id, default_upg_plan.id)
