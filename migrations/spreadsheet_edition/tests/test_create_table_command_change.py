from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.addons.base.maintenance.migrations.util import json


@change_version("saas~17.2")
class TestSpreadsheetCreateTableCommand(UpgradeCase):
    def prepare(self):
        command = {
            "type": "CREATE_FILTER_TABLE",
            "target": [{"top": 0, "left": 0, "bottom": 7, "right": 0}],
            "sheetId": "Sheet1",
        }

        revision_commands = {
            "type": "REMOTE_REVISION",
            "commands": [command],
        }

        revisions_insert = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 2,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_commands),
                    "parent_revision_id": "A",
                    "revision_id": "B",
                },
            ]
        )

        return revisions_insert.id

    def check(self, revision_id):
        revision = self.env["spreadsheet.revision"].browse(revision_id)

        commands = json.loads(revision.commands)["commands"]
        self.assertEqual(len(commands), 1, "There should be 1 commands in the revision")
        command = commands[0]

        self.assertEqual(command.get("type", None), "CREATE_TABLE")
        self.assertNotIn("target", command)
        self.assertEqual(
            command.get("ranges", None),
            [{"_sheetId": "Sheet1", "_zone": {"top": 0, "left": 0, "bottom": 7, "right": 0}}],
        )
