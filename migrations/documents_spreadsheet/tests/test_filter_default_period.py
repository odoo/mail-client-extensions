import json

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


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

        command_month = {
            "type": "ADD_GLOBAL_FILTER",
            "filter": {
                "id": "42",
                "type": "date",
                "label": "my filter",
                "rangeType": "month",
                "defaultsToCurrentPeriod": True,
            },
        }
        command_quarter = {
            "type": "ADD_GLOBAL_FILTER",
            "filter": {
                "id": "42",
                "type": "date",
                "label": "my filter",
                "rangeType": "quarter",
                "defaultsToCurrentPeriod": True,
            },
        }
        command_year = {
            "type": "ADD_GLOBAL_FILTER",
            "filter": {
                "id": "42",
                "type": "date",
                "label": "my filter",
                "rangeType": "year",
                "defaultsToCurrentPeriod": True,
            },
        }

        command_no_default = {
            "type": "ADD_GLOBAL_FILTER",
            "filter": {
                "id": "42",
                "type": "date",
                "label": "my filter",
                "rangeType": "year",
            },
        }

        revision_commands = {
            "type": "REMOTE_REVISION",
            "commands": [command_month, command_quarter, command_year, command_no_default],
        }

        revision = self.env["spreadsheet.revision"].create(
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

        return revision.id

    def check(self, revision_id):
        revision = self.env["spreadsheet.revision"].browse(revision_id)

        commands = json.loads(revision.commands)["commands"]
        self.assertEqual(len(commands), 4, "There should be 4 commands in the revision")
        command_month, command_quarter, command_year, command_no_default = commands

        self.assertEqual(command_month["filter"]["rangeType"], "fixedPeriod")
        self.assertEqual(command_month["filter"]["defaultValue"], "this_month")

        self.assertEqual(command_quarter["filter"]["rangeType"], "fixedPeriod")
        self.assertEqual(command_quarter["filter"]["defaultValue"], "this_quarter")

        self.assertEqual(command_year["filter"]["rangeType"], "fixedPeriod")
        self.assertEqual(command_year["filter"]["defaultValue"], "this_year")

        self.assertEqual(command_no_default["filter"]["rangeType"], "fixedPeriod")
        self.assertNotIn("defaultValue", command_no_default["filter"])
