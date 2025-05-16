from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.addons.base.maintenance.migrations.util import json


@change_version("saas~18.4")
class TestSpreadsheetChangeMoveConditionalFormatCommand(UpgradeCase):
    def prepare(self):
        if not util.table_exists(self.env.cr, "spreadsheet_revision") or not util.version_gte("saas~18.3"):
            return None

        add_command = {
            "type": "ADD_GLOBAL_FILTER",
            "filter": {
                "id": "42",
                "type": "text",
                "label": "my filter",
                "defaultValue": "hello",
            },
        }
        edit_command = {
            "filter": add_command["filter"],
            "type": "EDIT_GLOBAL_FILTER",
        }

        revision_commands = {
            "type": "REMOTE_REVISION",
            "commands": [add_command, edit_command],
        }

        revision = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 1,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_commands),
                    "parent_revision_id": False,
                    "revision_uuid": "abc",
                },
            ]
        )

        return revision.id

    def check(self, revision_id):
        if not revision_id:
            return
        revision = self.env["spreadsheet.revision"].browse(revision_id)

        commands = json.loads(revision.commands)["commands"]
        add_command, edit_command = commands

        self.assertEqual(add_command["filter"]["defaultValue"], ["hello"])
        self.assertEqual(edit_command["filter"]["defaultValue"], ["hello"])
