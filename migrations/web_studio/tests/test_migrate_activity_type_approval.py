import contextlib

with contextlib.suppress(ImportError):
    from odoo import Command

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.5")
class TestMigrateStudioActivityType(UpgradeCase):
    def prepare(self):
        user_group_field = "groups_id"
        if util.version_gte("saas~18.2"):
            user_group_field = "group_ids"

        test_user_manager = self.env["res.users"].create(
            {
                "login": "manager@test",
                "email": "manager@test",
                "name": "test_manager",
                user_group_field: [
                    Command.link(self.env.ref("base.group_user").id),
                    Command.link(self.env.ref("base.group_system").id),
                    Command.link(self.env.ref("base.group_partner_manager").id),
                ],
            }
        )
        test_user = self.env["res.users"].create(
            {
                "login": "test@test",
                "email": "test@test",
                "name": "test",
                user_group_field: [Command.link(self.env.ref("base.group_user").id)],
            }
        )
        rules = (
            self.env["studio.approval.rule"]
            .with_user(test_user_manager)
            .create(
                [
                    {
                        "model_id": self.env["ir.model"]._get("res.partner").id,
                        "method": "open_commercial_entity",
                        "approver_ids": [Command.link(test_user.id)],
                        "exclusive_user": True,
                    },
                ]
            )
        )
        rules[0].with_user(test_user_manager).check_approval(
            "res.partner", test_user.partner_id.id, "open_commercial_entity", None
        )
        activity = self.env["mail.activity"].search(
            [
                ("res_model", "=", "res.partner"),
                ("res_id", "=", test_user.partner_id.id),
                ("activity_type_id", "=", self.env.ref("web_studio.mail_activity_data_approve").id),
            ]
        )
        self.assertEqual(activity.activity_category, "grant_approval")
        return {"rule_ids": rules.ids, "activity_id": activity.id}

    def check(self, init):
        activity = self.env["mail.activity"].browse(init["activity_id"])
        self.assertEqual(activity.activity_type_id, self.env.ref("mail.mail_activity_data_todo"))
        self.assertEqual(activity.studio_approval_request_id.rule_id.id, init["rule_ids"][0])
