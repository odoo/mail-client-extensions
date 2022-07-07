# -*- coding: utf-8 -*-

import json

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.upgrade import util


@change_version("saas~15.5")
class TestSpreadsheetChangeAddCFCommand(UpgradeCase):
    def prepare(self):
        if not util.table_exists(self.env.cr, "spreadsheet_revision"):
            return
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

        command = {
            "type": "ADD_CONDITIONAL_FORMAT",
            "cf": {
                "rule": {
                    "type": "CellIsRule",
                    "operator": "IsNotEmpty",
                    "values": [],
                    "style": {"fillColor": "#b6d7a8"},
                },
                "id": "d7b9d518-85ec-4404-b746-79cbfc34ef08",
            },
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
                    "document_id": document.id,
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
        self.assertEqual(len(commands), 1, "There should be 1 commands in the revision")
        command = commands[0]

        self.assertNotIn("target", command)
        self.assertEqual(
            command.get("ranges", None),
            [{"_sheetId": "Sheet1", "_zone": {"top": 0, "left": 0, "bottom": 7, "right": 0}}],
        )
