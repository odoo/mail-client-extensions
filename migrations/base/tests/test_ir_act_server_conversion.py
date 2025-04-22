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


@change_version("saas~18.2")
class Test_03_Convert_Multi_Action(UpgradeCase):
    def prepare(self):
        A_values = {
            "name": "[A_Test_03_Convert_Multi_Action] Add country group",
            "model_id": self.env["ir.model"]._get("res.country").id,
            "state": "object_create",
            "crud_model_id": self.env["ir.model"]._get("res.country.group").id,
            "link_field_id": self.env["ir.model.fields"]._get("res.country", "country_group_ids").id,
            "value": "Test Group",
            "evaluation_type": "value",
        }
        B_values = {
            "name": "[B_Test_03_Convert_Multi_Action] Replace country currency with a new one",
            "model_id": self.env["ir.model"]._get("res.country").id,
            "state": "code",
            "code": """
new_record = env["res.currency"].create({"name": 'Test Currency', "symbol": "TC", "rate_ids": 2})
# link the new record to the current record
record.write({"currency_id": new_record.id})
""",
        }
        action_A = self.env["ir.actions.server"].create(A_values)
        action_B = self.env["ir.actions.server"].create(B_values)
        multi_1 = self.env["ir.actions.server"].create(
            {
                "name": "Multiple: add country group",
                "model_id": self.env["ir.model"]._get("res.country").id,
                "state": "multi",
                "child_ids": [Command.set([action_A.id])],
            }
        )
        multi_2 = self.env["ir.actions.server"].create(
            {
                "name": "Multiple: add country group and replace country currency",
                "model_id": self.env["ir.model"]._get("res.country").id,
                "state": "multi",
                "child_ids": [Command.set([action_A.id, action_B.id])],
            }
        )
        multi_3 = self.env["ir.actions.server"].create(
            {
                "name": "Multiple: add country group (bis)",
                "model_id": self.env["ir.model"]._get("res.country").id,
                "state": "multi",
                "child_ids": [Command.set([action_A.id])],
            }
        )

        A_xmlids = [
            {
                "model": "ir.actions.server",
                "module": "__testcase__",
                "name": name,
                "res_id": action_A.id,
            }
            for name in [
                "A_Test_03_Convert_Multi_Action_1",
                "A_Test_03_Convert_Multi_Action_2",
            ]
        ]
        B_xmlids = [
            {
                "model": "ir.actions.server",
                "module": "__testcase__",
                "name": name,
                "res_id": action_B.id,
            }
            for name in [
                "B_Test_03_Convert_Multi_Action_1",
                "B_Test_03_Convert_Multi_Action_2",
            ]
        ]
        self.env["ir.model.data"].create(A_xmlids + B_xmlids)
        return {
            "A_values": A_values,
            "B_values": B_values,
            "action_A_id": action_A.id,
            "action_B_id": action_B.id,
            "multi_1_id": multi_1.id,
            "multi_2_id": multi_2.id,
            "multi_3_id": multi_3.id,
        }

    def check(self, check):
        A_values = check["A_values"]
        B_values = check["B_values"]
        multi_1 = self.env["ir.actions.server"].browse(check["multi_1_id"])
        multi_2 = self.env["ir.actions.server"].browse(check["multi_2_id"])
        multi_3 = self.env["ir.actions.server"].browse(check["multi_3_id"])
        A_actions = self.env["ir.actions.server"].search([("name", "=", A_values["name"])])
        B_actions = self.env["ir.actions.server"].search([("name", "=", B_values["name"])])
        A_actions = A_actions.sorted(lambda r: r.parent_id.id)

        # "A" actions should have been duplicated
        self.assertRecordValues(
            A_actions,
            [
                {**A_values, "parent_id": False},
                {**A_values, "parent_id": multi_1.id},
                {**A_values, "parent_id": multi_2.id},
                {**A_values, "parent_id": multi_3.id},
            ],
        )
        # Orphan action is the original one
        self.assertRecordValues(
            A_actions[0],
            [{**A_values, "parent_id": False, "id": check["action_A_id"]}],
        )

        # "B" actions should not have been duplicated
        self.assertRecordValues(
            B_actions,
            [{**B_values, "parent_id": multi_2.id}],
        )

        A_xmlids = self.env["ir.model.data"].search(
            [
                ("model", "=", "ir.actions.server"),
                ("res_id", "in", A_actions.ids),
            ]
        )
        self.assertItemsEqual(
            [f"{xmlid.module}.{xmlid.name}" for xmlid in A_xmlids],
            [
                "__testcase__.A_Test_03_Convert_Multi_Action_1",
                "__testcase__.A_Test_03_Convert_Multi_Action_2",
                f"__upgrade__.A_Test_03_Convert_Multi_Action_1__copy__{multi_1.id}__{A_actions[1].id}",
                f"__cloc_exclude__.A_Test_03_Convert_Multi_Action_1__copy__{multi_1.id}__{A_actions[1].id}",
                f"__upgrade__.A_Test_03_Convert_Multi_Action_2__copy__{multi_1.id}__{A_actions[1].id}",
                f"__cloc_exclude__.A_Test_03_Convert_Multi_Action_2__copy__{multi_1.id}__{A_actions[1].id}",
                f"__upgrade__.A_Test_03_Convert_Multi_Action_1__copy__{multi_2.id}__{A_actions[2].id}",
                f"__cloc_exclude__.A_Test_03_Convert_Multi_Action_1__copy__{multi_2.id}__{A_actions[2].id}",
                f"__upgrade__.A_Test_03_Convert_Multi_Action_2__copy__{multi_2.id}__{A_actions[2].id}",
                f"__cloc_exclude__.A_Test_03_Convert_Multi_Action_2__copy__{multi_2.id}__{A_actions[2].id}",
                f"__upgrade__.A_Test_03_Convert_Multi_Action_1__copy__{multi_3.id}__{A_actions[3].id}",
                f"__cloc_exclude__.A_Test_03_Convert_Multi_Action_1__copy__{multi_3.id}__{A_actions[3].id}",
                f"__upgrade__.A_Test_03_Convert_Multi_Action_2__copy__{multi_3.id}__{A_actions[3].id}",
                f"__cloc_exclude__.A_Test_03_Convert_Multi_Action_2__copy__{multi_3.id}__{A_actions[3].id}",
            ],
        )
        B_xmlids = self.env["ir.model.data"].search(
            [
                ("model", "=", "ir.actions.server"),
                ("res_id", "in", B_actions.ids),
            ]
        )
        self.assertItemsEqual(
            [f"{xmlid.module}.{xmlid.name}" for xmlid in B_xmlids],
            [
                "__testcase__.B_Test_03_Convert_Multi_Action_1",
                "__testcase__.B_Test_03_Convert_Multi_Action_2",
            ],
        )

        # The following assertion is not *directly* related to the testing data.
        # It is here to verify that there is no __upgrade__ xmlid left for
        # duplicated standard actions. That way we are making sure that we are
        # not leaving unmatched duplicates for standard stuff.
        # If you read this, you should take a look at the following helper
        # function: rematch_xmlids (in base/saas~18.2.1.3/pre-ir_act_server.py).
        # Use it if needed with util.import_script
        # Note that if assertion fails, it could be a false positive if you played with your dev db.
        upgrade_xmlids = self.env["ir.model.data"].search(
            [
                ("model", "=", "ir.actions.server"),
                ("module", "=", "__upgrade__"),
                # ignore test xmlids
                ("id", "not in", A_xmlids.ids),
                # ignore upgrade crons (see util.create_cron)
                ("name", "not =ilike", "cron_post_upgrade%"),
            ]
        )
        self.assertFalse(upgrade_xmlids, "Extra xmlids: " + ", ".join(f"{r.module}.{r.name}" for r in upgrade_xmlids))
