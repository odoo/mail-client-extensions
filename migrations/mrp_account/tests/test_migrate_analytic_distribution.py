import contextlib

with contextlib.suppress(ImportError):
    from odoo import Command

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.5")
class TestMigrateAnalyticDistribution(UpgradeCase):
    def prepare(self):
        product_a, product_b, product_c, product_d, product_e = self.env["product.product"].create(
            [
                {"name": "Product A"},
                {"name": "Product B"},
                {"name": "Product C"},
                {"name": "Product D"},
                {"name": "Product E"},
            ]
        )
        workcenter = self.env["mrp.workcenter"].create(
            {
                "name": "Nuclear Workcenter",
                "default_capacity": 2,
                "time_start": 10,
                "time_stop": 5,
                "time_efficiency": 80,
            }
        )
        project_plan, other_plans = self.env["account.analytic.plan"]._get_all_plans()
        if not project_plan:
            project_plan = self.env["account.analytic.plan"].create({"name": "Test project plan"})
        if not other_plans:
            other_plans = self.env["account.analytic.plan"].create({"name": "Test other plan"})
        analytic_accounts = analytic_account_1, analytic_account_2, analytic_account_3 = self.env[
            "account.analytic.account"
        ].create(
            [
                {"name": "Test Account 1", "plan_id": project_plan.id},
                {"name": "Test Account 2", "plan_id": project_plan.id},
                {"name": "Test Account 3", "plan_id": other_plans[0].id},
            ]
        )
        boms = bom1, bom2, bom3, bom4 = self.env["mrp.bom"].create(
            [
                {
                    "product_id": product_a.id,
                    "product_tmpl_id": product_a.product_tmpl_id.id,
                    "product_qty": 4,
                    "consumption": "flexible",
                    "analytic_distribution": False,
                    "operation_ids": [
                        Command.create({"name": "Test Operation", "workcenter_id": workcenter.id, "time_cycle": 15}),
                    ],
                    "type": "normal",
                    "bom_line_ids": [
                        Command.create({"product_id": product_b.id, "product_qty": 1}),
                    ],
                },
                {
                    "product_id": product_b.id,
                    "product_tmpl_id": product_b.product_tmpl_id.id,
                    "product_qty": 2,
                    "consumption": "flexible",
                    "analytic_distribution": {analytic_account_1.id: 100},
                    "operation_ids": [
                        Command.create({"name": "Test Operation", "workcenter_id": workcenter.id, "time_cycle": 15}),
                    ],
                    "type": "normal",
                    "bom_line_ids": [
                        Command.create({"product_id": product_c.id, "product_qty": 2}),
                    ],
                },
                {
                    "product_id": product_c.id,
                    "product_tmpl_id": product_c.product_tmpl_id.id,
                    "product_qty": 2,
                    "consumption": "flexible",
                    "analytic_distribution": {analytic_account_1.id: 100, analytic_account_2.id: 20},
                    "operation_ids": [
                        Command.create({"name": "Test Operation", "workcenter_id": workcenter.id, "time_cycle": 15}),
                    ],
                    "type": "normal",
                    "bom_line_ids": [
                        Command.create({"product_id": product_d.id, "product_qty": 3}),
                    ],
                },
                {
                    "product_id": product_d.id,
                    "product_tmpl_id": product_d.product_tmpl_id.id,
                    "product_qty": 1,
                    "consumption": "flexible",
                    "analytic_distribution": {
                        analytic_account_1.id: 100,
                        analytic_account_2.id: 20,
                        analytic_account_3.id: 50,
                    },
                    "operation_ids": [
                        Command.create({"name": "Test Operation", "workcenter_id": workcenter.id, "time_cycle": 15}),
                    ],
                    "type": "normal",
                    "bom_line_ids": [
                        Command.create({"product_id": product_e.id, "product_qty": 3}),
                    ],
                },
            ]
        )
        productions = self.env["mrp.production"].create(
            [
                {"product_id": product_a.id, "bom_id": bom1.id, "product_qty": 1},
                {"product_id": product_b.id, "bom_id": bom2.id, "product_qty": 1},
                {
                    "product_id": product_c.id,
                    "bom_id": bom3.id,
                    "product_qty": 1,
                    "analytic_distribution": {analytic_account_1.id: 80},
                },
                {
                    "product_id": product_a.id,
                    "bom_id": bom1.id,
                    "product_qty": 1,
                    "analytic_distribution": {f"{analytic_account_2.id},{analytic_account_3.id}": 100},
                },
                {
                    "product_id": product_d.id,
                    "bom_id": bom4.id,
                    "product_qty": 1,
                    "analytic_distribution": {
                        analytic_account_1.id: 100,
                        analytic_account_2.id: 20,
                        analytic_account_3.id: 100,
                    },
                },
            ]
        )

        return (
            (project_plan + other_plans[0]).ids,
            analytic_accounts.ids,
            boms.ids,
            productions.ids,
        )

    def check(self, init):
        self.assertTrue(util.module_installed(self.env.cr, "project_mrp"))

        analytic_plan_ids, analytic_account_ids, bom_ids, production_ids = init
        project_plan, other_plan = self.env["account.analytic.plan"].browse(analytic_plan_ids)
        bom1, bom2, bom3, bom4 = self.env["mrp.bom"].browse(bom_ids)
        production1, production2, production3, production4, production5 = self.env["mrp.production"].browse(
            production_ids
        )
        analytic_account_1, analytic_account_2, analytic_account_3 = self.env["account.analytic.account"].browse(
            analytic_account_ids
        )
        self.assertFalse(bom1.project_id, "No project should be generated since there is no analytic distribution set.")

        self.assertTrue(
            bom2.project_id,
            "A project should be generated since the analytic distribution contains only one line at 100 percent.",
        )
        self.assertFalse(bom2.project_id.active, "The generated project should be archived.")
        project_bom2 = bom2.project_id
        self.assertEqual(
            project_bom2[project_plan._column_name()],
            analytic_account_1,
            "The analytic account set in the analytic distribution for the project plan should be set in project plan of the generated project.",
        )
        self.assertFalse(
            project_bom2[other_plan._column_name()], "No analytic account should be set on that analytic plan."
        )

        self.assertFalse(
            bom3.project_id,
            "No project should be generated since the analytic distribution set does not contain only one line at 100.",
        )

        self.assertFalse(
            bom4.project_id,
            "No project should be generated since there is more than one line in the analytic distribution.",
        )

        self.assertFalse(
            production1.project_id, "No project should be generated since there is no analytic distribution set."
        )

        self.assertTrue(
            production2.project_id, "A project should be set on that MO (should be the same than the bom linked)."
        )
        self.assertEqual(
            production2.project_id, bom2.project_id, "The project set should be the one generated for the bom linked."
        )

        self.assertFalse(
            production3.project_id,
            "No project should be generated since the analytic distribution did not contain only one line at 100 percent.",
        )

        self.assertTrue(
            production4.project_id,
            "A project should be generated since the analytic distribution set only had a line at 100 percent.",
        )
        self.assertFalse(production4.project_id.active, "The generated project should be archived.")
        self.assertNotEqual(
            production4.project_id, project_bom2, "The project generated is not the same than MO 2 and BOM 2."
        )
        project_production4 = production4.project_id
        self.assertEqual(
            project_production4[project_plan._column_name()],
            analytic_account_2,
            "The analytic account set in the analytic distribution for the project plan should be set in project plan of the generated project.",
        )
        self.assertEqual(
            project_production4[other_plan._column_name()],
            analytic_account_3,
            "The analytic account set in the analytic distribution for the other plan should be set in other plan of the generated project.",
        )

        self.assertFalse(
            production5.project_id,
            "No project should be generated since there is more than one line in the analytic distribution.",
        )
