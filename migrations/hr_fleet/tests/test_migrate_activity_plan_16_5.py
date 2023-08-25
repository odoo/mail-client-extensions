# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.addons.base.maintenance.migrations.util import version_gte


@change_version("saas~16.5")
class TestMigrateActivityPlan(UpgradeCase):

    def prepare(self):
        fleet_manager_supported = version_gte("saas~16.2")
        plan = self.env["hr.plan"].create(
            {
                "name": "hr_fleet_test_migration_activity_plan_simple_plan",
                "plan_activity_type_ids": [(0, 0, {
                    "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
                    "responsible": "fleet_manager" if fleet_manager_supported else "coach",
                })],
            }
        )

        return {
            "plan_id": plan.id,
            "fleet_manager_supported": fleet_manager_supported,
        }

    def check(self, init):
        plan = self.env["mail.activity.plan"].browse(init["plan_id"])
        self.assertEqual(plan.res_model, "hr.employee")
        self.assertEqual(
            plan.template_ids[0].responsible_type, "fleet_manager" if init["fleet_manager_supported"] else "coach"
        )
