import json

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.3")
class TestSpreadsheetRemovePivotPosition(UpgradeCase):
    def prepare(self):
        if not util.table_exists(self.env.cr, "spreadsheet_revision"):
            return None

        command_1 = {
            "type": "UPDATE_CELL",
            "sheetId": "Sheet1",
            "content": '=-PIVOT.VALUE("1","balance","account_id",ODOO.PIVOT.POSITION("1","account_id",12),"date:quarter","4/"&ODOO.FILTER.VALUE("Year"))',
            "row": 1,
            "col": 1,
        }
        command_2 = {
            "type": "UPDATE_CELL",
            "sheetId": "Sheet1",
            "content": '=PIVOT.HEADER("1","account_id",ODOO.PIVOT.POSITION("1","account_id",14))',
            "row": 2,
            "col": 1,
        }
        command_3 = {
            "type": "UPDATE_CELL",
            "sheetId": "Sheet1",
            "content": '=ODOO.PIVOT.POSITION("1","account_id",14)',
            "row": 3,
            "col": 1,
        }
        command_4 = {
            "type": "UPDATE_CELL",
            "sheetId": "Sheet1",
            "content": '=ODOO.PIVOT.POSITION("1",14)',
            "row": 4,
            "col": 1,
        }

        revision_commands = {
            "type": "REMOTE_REVISION",
            "commands": [command_1, command_2, command_3, command_4],
        }

        field_name = "revision_uuid" if util.version_gte("saas~17.2") else "revision_id"

        revisions_insert = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 6565456,  # arbitrary value
                    "res_model": "spreadsheet.template",
                    "commands": json.dumps(revision_commands),
                    field_name: "B",
                    "parent_revision_id": False if util.version_gte("saas~17.2") else "START_REVISION",
                },
            ]
        )
        return revisions_insert.id

    def check(self, revision_id):
        if not revision_id:
            return
        revision = self.env["spreadsheet.revision"].browse(revision_id)

        commands = json.loads(revision.commands)["commands"]
        self.assertEqual(len(commands), 4, "There should be 4 commands in the revision")

        results = [
            '=-PIVOT.VALUE("1","balance","#account_id",12,"date:quarter","4/"&ODOO.FILTER.VALUE("Year"))',
            '=PIVOT.HEADER("1","#account_id",14)',
            '=ODOO.PIVOT.POSITION("1","account_id",14)',
            '=ODOO.PIVOT.POSITION("1",14)',
        ]

        for result, command in zip(results, commands):
            self.assertEqual(command["content"], result)
