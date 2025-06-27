from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.addons.base.maintenance.migrations.util import json


@change_version("saas~18.5")
class TestDefaultValueFilter(UpgradeCase):
    def prepare(self):
        if not util.version_gte("saas~18.5"):
            self.skipTest("Spreadsheet default value test is skipped for source versions < saas~18.5")

        commands = [
            {
                "type": "ADD_GLOBAL_FILTER",
                "filter": {
                    "id": "42",
                    "type": "text",
                    "label": "my filter",
                    "defaultValue": ["hello"],
                },
            },
            {
                "type": "ADD_GLOBAL_FILTER",
                "filter": {
                    "id": "43",
                    "type": "relation",
                    "modelName": "res.partner",
                    "label": "my filter",
                    "defaultValue": [1, 2],
                },
            },
            {
                "type": "ADD_GLOBAL_FILTER",
                "filter": {
                    "id": "44",
                    "type": "relation",
                    "modelName": "res.company",
                    "label": "my filter",
                    "includeChildren": True,
                    "defaultValue": [3, 4],
                },
            },
            {
                "type": "ADD_GLOBAL_FILTER",
                "filter": {
                    "id": "45",
                    "type": "boolean",
                    "label": "my filter",
                    "defaultValue": [True],
                },
            },
            {
                "type": "ADD_GLOBAL_FILTER",
                "filter": {
                    "id": "46",
                    "type": "boolean",
                    "label": "my filter",
                    "defaultValue": [False],
                },
            },
            {
                "type": "ADD_GLOBAL_FILTER",
                "filter": {
                    "id": "47",
                    "type": "boolean",
                    "label": "my filter",
                    "defaultValue": [True, False],
                },
            },
        ]

        revision_commands = {
            "type": "REMOTE_REVISION",
            "commands": commands,
        }

        revision = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 422,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_commands),
                    "parent_revision_id": False,
                    "revision_uuid": "abcdefgh",
                },
            ]
        )

        return revision.id

    def check(self, revision_id):
        revision = self.env["spreadsheet.revision"].browse(revision_id)
        commands = json.loads(revision.commands)["commands"]
        self.assertEqual(commands[0]["filter"]["defaultValue"], {"operator": "ilike", "strings": ["hello"]})
        self.assertEqual(commands[1]["filter"]["defaultValue"], {"operator": "in", "ids": [1, 2]})
        self.assertEqual(commands[2]["filter"]["defaultValue"], {"operator": "child_of", "ids": [3, 4]})
        self.assertEqual(commands[3]["filter"]["defaultValue"], {"operator": "set"})
        self.assertEqual(commands[4]["filter"]["defaultValue"], {"operator": "not_set"})
        self.assertFalse("defaultValue" in commands[5]["filter"])
