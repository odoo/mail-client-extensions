from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.addons.base.maintenance.migrations.util import json


@change_version("saas~17.2")
class TestSpreadsheetRemoveTableCommand(UpgradeCase):
    def prepare(self):
        remove_table_command = {
            "type": "REMOVE_FILTER_TABLE",
            "sheetId": "Sheet1",
            "target": [{"top": 0, "left": 0, "bottom": 7, "right": 0}],
        }

        revision_commands = {
            "type": "REMOTE_REVISION",
            "commands": [remove_table_command],
        }

        revisions_insert = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 98723,
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
        remove_table_command = commands[0]

        self.assertEqual(remove_table_command.get("type", None), "REMOVE_TABLE")
        self.assertEqual(remove_table_command.get("target", None), [{"top": 0, "left": 0, "bottom": 7, "right": 0}])
