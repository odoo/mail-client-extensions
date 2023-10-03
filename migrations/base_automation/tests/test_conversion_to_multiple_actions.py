# -*- coding: utf-8 -*-

try:
    from odoo import Command
except ImportError:
    Command = None

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.5")
class Test_00_SimpleAutomation(UpgradeCase):
    MODEL, FIELD = "mail.blacklist", "email"

    def prepare(self):
        automation = self.env["base.automation"].create(
            {
                "name": f"Force Archived {self.MODEL}",
                "trigger": "on_create_or_write",
                "model_id": self.env["ir.model"]._get(self.MODEL).id,
                "type": "ir.actions.server",
                "trigger_field_ids": [Command.set([self.env["ir.model.fields"]._get(self.MODEL, self.FIELD).id])],
                "fields_lines": [
                    Command.create(
                        {
                            "col1": self.env["ir.model.fields"]._get(self.MODEL, "active").id,
                            "evaluation_type": "equation",
                            "value": "False",
                        }
                    )
                ],
            }
        )
        return {
            "automation_id": automation.id,
        }

    def check(self, check):
        automation = self.env["base.automation"].browse(check["automation_id"])
        self.assertRecordValues(
            automation,
            [
                {
                    "name": f"Force Archived {self.MODEL}",
                    "trigger": "on_create_or_write",
                    "model_id": self.env["ir.model"]._get(self.MODEL).id,
                    "model_name": self.MODEL,
                    "trigger_field_ids": [self.env["ir.model.fields"]._get(self.MODEL, self.FIELD).id],
                }
            ],
        )
        self.assertEqual(len(automation.action_server_ids), 1)
        action = automation.action_server_ids[0]
        self.assertRecordValues(
            action,
            [
                {
                    "name": f"Force Archived {self.MODEL}",
                    "model_id": self.env["ir.model"]._get(self.MODEL).id,
                    "model_name": self.MODEL,
                    "state": "code",
                    "code": """record.write({"active": False})""",
                    "evaluation_type": False,
                    "value": False,
                }
            ],
        )


@change_version("saas~16.5")
class Test_01_Deprecate_OnCreate_Automation(UpgradeCase):
    def prepare(self):
        automation = self.env["base.automation"].create(
            {
                "active": True,
                "name": "Test",
                "trigger": "on_create",
                "model_id": self.env.ref("base.model_res_partner").id,
                "state": "code",
                "code": "",  # no-op action
            }
        )
        self.assertEqual(automation.active, True)
        return {
            "automation_id": automation.id,
        }

    def check(self, check):
        automation = self.env["base.automation"].browse(check["automation_id"])
        self.assertRecordValues(
            automation,
            [
                {
                    "active": False,
                    "name": "Test",
                    "trigger": "on_create",
                    "model_id": self.env.ref("base.model_res_partner").id,
                }
            ],
        )
        self.assertEqual(len(automation.action_server_ids), 1)
        action = automation.action_server_ids[0]
        self.assertRecordValues(
            action,
            [
                {
                    "name": "Test",
                    "model_id": self.env.ref("base.model_res_partner").id,
                    "state": "code",
                    "code": "",  # no-op action
                }
            ],
        )


@change_version("saas~16.5")
class Test_02_Deprecate_OnWrite_Automation(UpgradeCase):
    def prepare(self):
        automation = self.env["base.automation"].create(
            {
                "active": True,
                "name": "Test",
                "trigger": "on_write",
                "model_id": self.env.ref("base.model_res_partner").id,
                "state": "code",
                "code": "",  # no-op action
            }
        )
        self.assertEqual(automation.active, True)
        return {
            "automation_id": automation.id,
        }

    def check(self, check):
        automation = self.env["base.automation"].browse(check["automation_id"])
        self.assertRecordValues(
            automation,
            [
                {
                    "active": False,
                    "name": "Test",
                    "trigger": "on_write",
                    "model_id": self.env.ref("base.model_res_partner").id,
                }
            ],
        )
        self.assertEqual(len(automation.action_server_ids), 1)
        action = automation.action_server_ids[0]
        self.assertRecordValues(
            action,
            [
                {
                    "name": "Test",
                    "model_id": self.env.ref("base.model_res_partner").id,
                    "state": "code",
                    "code": "",  # no-op action
                }
            ],
        )
