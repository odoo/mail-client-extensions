import json

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("16.2")
class TestSpreadsheetChangeMoveSheetCommand(UpgradeCase):
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

        command_left = {
            "type": "MOVE_SHEET",
            "direction": "left",
            "sheetId": "Sheet1",
        }

        command_right = {
            "type": "MOVE_SHEET",
            "direction": "right",
            "sheetId": "Sheet1",
        }

        revision_commands = {
            "type": "REMOTE_REVISION",
            "commands": [command_left, command_right],
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

        command_left = commands[0]
        self.assertNotIn("direction", command_left)
        self.assertEqual(command_left.get("delta", None), -1)

        command_right = commands[1]
        self.assertNotIn("direction", command_right)
        self.assertEqual(command_right.get("delta", None), 1)
