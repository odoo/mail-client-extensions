# -*- coding: utf-8 -*-

try:
    from odoo import Command
except ImportError:
    Command = None

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.5")
class Test_00_SimpleAutomation(UpgradeCase):
    def prepare(self):
        automation = self.env["base.automation"].create(
            {
                "name": "Force Archived Contacts",
                "trigger": "on_create_or_write",
                "model_id": self.env.ref("base.model_res_partner").id,
                "type": "ir.actions.server",
                "trigger_field_ids": [Command.set([self.env.ref("base.field_res_partner__name").id])],
                "fields_lines": [
                    Command.create(
                        {
                            "col1": self.env.ref("base.field_res_partner__active").id,
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
                    "name": "Force Archived Contacts",
                    "trigger": "on_create_or_write",
                    "model_id": self.env.ref("base.model_res_partner").id,
                    "model_name": "res.partner",
                    "trigger_field_ids": [self.env.ref("base.field_res_partner__name").id],
                }
            ],
        )
        self.assertEqual(len(automation.action_server_ids), 1)
        action = automation.action_server_ids[0]
        self.assertRecordValues(
            action,
            [
                {
                    "name": "Force Archived Contacts",
                    "model_id": self.env.ref("base.model_res_partner").id,
                    "model_name": "res.partner",
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
