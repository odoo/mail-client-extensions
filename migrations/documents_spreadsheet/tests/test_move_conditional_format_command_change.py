from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.addons.base.maintenance.migrations.util import json


@change_version("saas~16.5")
class TestSpreadsheetChangeMoveConditionalFormatCommand(UpgradeCase):
    def prepare(self):
        if not util.table_exists(self.env.cr, "spreadsheet_revision"):
            return None
        folder = self.env["documents.folder"].create(
            {
                "name": "folder",
            }
        )
        document = self.env["documents.document"].create(
            {
                "folder_id": folder.id,
            }
        )

        command_up = {
            "type": "MOVE_CONDITIONAL_FORMAT",
            "direction": "up",
            "sheetId": "Sheet1",
        }

        command_down = {
            "type": "MOVE_CONDITIONAL_FORMAT",
            "direction": "down",
            "sheetId": "Sheet1",
        }

        revision_commands = {
            "type": "REMOTE_REVISION",
            "commands": [command_up, command_down],
        }

        revisions_insert = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": document.id,
                    "res_model": "documents.document",
                    "commands": json.dumps(revision_commands),
                    "parent_revision_id": "A",
                    "revision_id": "B",
                },
            ]
        )

        return revisions_insert.id

    def check(self, revision_id):
        if not revision_id:
            return
        revision = self.env["spreadsheet.revision"].browse(revision_id)

        commands = json.loads(revision.commands)["commands"]
        self.assertEqual(len(commands), 2, "There should be 2 commands in the revision")

        command_up = commands[0]
        self.assertEqual(command_up.get("type", None), "CHANGE_CONDITIONAL_FORMAT_PRIORITY")
        self.assertNotIn("direction", command_up)
        self.assertEqual(command_up.get("delta", None), 1)

        command_down = commands[1]
        self.assertEqual(command_down.get("type", None), "CHANGE_CONDITIONAL_FORMAT_PRIORITY")
        self.assertNotIn("direction", command_down)
        self.assertEqual(command_down.get("delta", None), -1)
