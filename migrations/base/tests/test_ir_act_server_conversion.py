try:
    from odoo import Command
except ImportError:
    Command = None

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.5")
class Test_01_Convert_ObjectCreate_Action(UpgradeCase):
    def prepare(self):
        action = self.env["ir.actions.server"].create(
            {
                "name": "Replace country currency with a new one",
                "model_id": self.env.ref("base.model_res_country").id,
                "state": "object_create",
                "crud_model_id": self.env.ref("base.model_res_currency").id,
                "link_field_id": self.env.ref("base.field_res_country__currency_id").id,
                "fields_lines": [
                    Command.create(
                        {
                            "col1": self.env.ref("base.field_res_currency__name").id,
                            "evaluation_type": "value",
                            "value": "Test Currency",
                        }
                    ),
                    Command.create(
                        {
                            "col1": self.env.ref("base.field_res_currency__symbol").id,
                            "evaluation_type": "equation",
                            "value": '"TC"',
                        }
                    ),
                    Command.create(
                        {
                            "col1": self.env.ref("base.field_res_currency__rate_ids").id,
                            "evaluation_type": "reference",
                            "value": "2",
                        }
                    ),
                ],
            }
        )
        return {
            "action_id": action.id,
        }

    def check(self, check):
        action_id = check["action_id"]
        action = self.env["ir.actions.server"].browse(action_id)
        self.assertRecordValues(
            action,
            [
                {
                    "name": "Replace country currency with a new one",
                    "model_id": self.env.ref("base.model_res_country").id,
                    "state": "code",
                    "crud_model_id": None,
                    "link_field_id": None,
                    "code": """
new_record = env["res.currency"].create({"name": 'Test Currency', "symbol": "TC", "rate_ids": 2})
# link the new record to the current record
record.write({"currency_id": new_record.id})
""",
                }
            ],
        )


@change_version("saas~16.5")
class Test_01bis_Convert_ObjectCreate_Action(UpgradeCase):
    def prepare(self):
        action = self.env["ir.actions.server"].create(
            {
                "name": "Add country group on country creation",
                "model_id": self.env["ir.model"]._get("res.country").id,
                "state": "object_create",
                "crud_model_id": self.env["ir.model"]._get("res.country.group").id,
                "link_field_id": self.env["ir.model.fields"]._get("res.country", "country_group_ids").id,
                "fields_lines": [
                    Command.create(
                        {
                            "col1": self.env["ir.model.fields"]._get("res.country.group", "name").id,
                            "evaluation_type": "value",
                            "value": "Test Group",
                        }
                    ),
                ],
            }
        )
        return {
            "action_id": action.id,
        }

    def check(self, check):
        action_id = check["action_id"]
        action = self.env["ir.actions.server"].browse(action_id)
        self.assertRecordValues(
            action,
            [
                {
                    "name": "Add country group on country creation",
                    "model_id": self.env["ir.model"]._get("res.country").id,
                    "state": "object_create",
                    "crud_model_id": self.env["ir.model"]._get("res.country.group").id,
                    "link_field_id": self.env["ir.model.fields"]._get("res.country", "country_group_ids").id,
                    "update_field_id": None,
                    "value": "Test Group",
                    "evaluation_type": "value",
                }
            ],
        )


@change_version("saas~16.5")
class Test_01ter_Convert_ObjectCreate_Action(UpgradeCase):
    def prepare(self):
        action = self.env["ir.actions.server"].create(
            {
                "name": "Add country group on country creation: python expression",
                "model_id": self.env["ir.model"]._get("res.country").id,
                "state": "object_create",
                "crud_model_id": self.env["ir.model"]._get("res.country.group").id,
                "link_field_id": self.env["ir.model.fields"]._get("res.country", "country_group_ids").id,
                "fields_lines": [
                    Command.create(
                        {
                            "col1": self.env["ir.model.fields"]._get("res.country.group", "name").id,
                            "evaluation_type": "equation",
                            "value": "'Test Group: ' + record.name",
                        }
                    ),
                ],
            }
        )
        return {
            "action_id": action.id,
        }

    def check(self, check):
        action_id = check["action_id"]
        action = self.env["ir.actions.server"].browse(action_id)
        self.assertRecordValues(
            action,
            [
                {
                    "name": "Add country group on country creation: python expression",
                    "model_id": self.env["ir.model"]._get("res.country").id,
                    "state": "code",
                    "crud_model_id": None,
                    "link_field_id": None,
                    "code": """
new_record = env["res.country.group"].create({"name": 'Test Group: ' + record.name})
# link the new record to the current record
record.write({"country_group_ids": [Command.link(new_record.id)]})
""",
                    "update_field_id": None,
                    "value": False,
                    "evaluation_type": False,
                }
            ],
        )


@change_version("saas~16.5")
class Test_02_Convert_ObjectWrite_Action(UpgradeCase):
    def prepare(self):
        action = self.env["ir.actions.server"].create(
            {
                "name": "Update currency",
                "model_id": self.env.ref("base.model_res_currency").id,
                "state": "object_write",
                "fields_lines": [
                    Command.create(
                        {
                            "col1": self.env.ref("base.field_res_currency__name").id,
                            "evaluation_type": "value",
                            "value": "Test Currency",
                        }
                    ),
                    Command.create(
                        {
                            "col1": self.env.ref("base.field_res_currency__symbol").id,
                            "evaluation_type": "equation",
                            "value": '"TC"',
                        }
                    ),
                ],
            }
        )
        return {
            "action_id": action.id,
        }

    def check(self, check):
        action_id = check["action_id"]
        action = self.env["ir.actions.server"].browse(action_id)
        self.assertRecordValues(
            action,
            [
                {
                    "name": "Update currency",
                    "model_id": self.env.ref("base.model_res_currency").id,
                    "state": "code",
                    "code": """record.write({"name": 'Test Currency', "symbol": "TC"})""",
                }
            ],
        )


@change_version("saas~16.5")
class Test_02bis_Convert_ObjectWrite_Action(UpgradeCase):
    def prepare(self):
        action = self.env["ir.actions.server"].create(
            {
                "name": "Append ! to currency name",
                "model_id": self.env["ir.model"]._get("res.currency").id,
                "state": "object_write",
                "fields_lines": [
                    Command.create(
                        {
                            "col1": self.env["ir.model.fields"]._get("res.currency", "name").id,
                            "evaluation_type": "equation",
                            "value": "record.name + '!'",
                        }
                    ),
                ],
            }
        )
        return {
            "action_id": action.id,
        }

    def check(self, check):
        action_id = check["action_id"]
        action = self.env["ir.actions.server"].browse(action_id)
        self.assertRecordValues(
            action,
            [
                {
                    "name": "Append ! to currency name",
                    "model_id": self.env["ir.model"]._get("res.currency").id,
                    "state": "object_write",
                    "update_field_id": self.env["ir.model.fields"]._get("res.currency", "name").id,
                    "evaluation_type": "equation",
                    "value": "record.name + '!'",
                }
            ],
        )
