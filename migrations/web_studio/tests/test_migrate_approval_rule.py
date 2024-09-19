import contextlib

with contextlib.suppress(ImportError):
    from odoo import Command

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.5")
class TestMigrateResponsible(UpgradeCase):
    def prepare(self):
        test_user_manager = self.env["res.users"].create(
            {
                "login": "manager@test",
                "name": "test_manager",
                "groups_id": [
                    Command.link(self.env.ref("base.group_user").id),
                    Command.link(self.env.ref("base.group_system").id),
                ],
            }
        )
        test_user = self.env["res.users"].create(
            {"login": "test@test", "name": "test", "groups_id": [Command.link(self.env.ref("base.group_user").id)]}
        )
        rule = (
            self.env["studio.approval.rule"]
            .with_user(test_user_manager)
            .create(
                {
                    "model_id": self.env["ir.model"]._get("res.partner").id,
                    "method": "open_commercial_entity",
                    "responsible_id": test_user.id,
                }
            )
        )
        return {"rule_id": rule.id, "manager_id": test_user_manager.id, "test_user_id": test_user.id}

    def check(self, init):
        rule = self.env["studio.approval.rule"].browse(init["rule_id"])
        self.assertEqual(len(rule.approver_log_ids), 2)

        logs = sorted(rule.approver_log_ids, key=lambda log: log.user_id.id)

        self.assertEqual(logs[0].user_id.id, init["manager_id"])
        self.assertEqual(logs[0].create_uid.id, init["manager_id"])

        self.assertEqual(logs[1].user_id.id, init["test_user_id"])
        self.assertEqual(logs[1].create_uid.id, init["manager_id"])

        self.assertEqual(rule.approver_ids, self.env["res.users"].browse([init["manager_id"], init["test_user_id"]]))

        self.assertEqual(rule.users_to_notify, self.env["res.users"].browse([init["manager_id"], init["test_user_id"]]))
