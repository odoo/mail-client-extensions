from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.5")
class TestMigrateAnalyticAccountId(UpgradeCase):
    def prepare(self):
        plan = self.env["account.analytic.plan"].create({"name": "Test Plan"})
        account = self.env["account.analytic.account"].create(
            {
                "name": "Test Account",
                "plan_id": plan.id,
            }
        )
        project = self.env["project.project"].create(
            {
                "name": "Test Project",
                "analytic_account_id": account.id,
            }
        )
        return (project.id, account.id, plan.id)

    def check(self, init):
        project_id, account_id, plan_id = init
        project = self.env["project.project"].browse(project_id)
        plan = self.env["account.analytic.plan"].browse(plan_id)
        self.assertEqual(project.account_id.id, account_id)
        self.assertEqual(project[plan._column_name()].id, account_id)
