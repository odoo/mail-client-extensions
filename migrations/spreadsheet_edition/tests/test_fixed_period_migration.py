from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.addons.base.maintenance.migrations.util import json


@change_version("saas~18.4")
class TestSpreadsheetFixedPeriod(UpgradeCase):
    def prepare(self):
        if not util.table_exists(self.env.cr, "spreadsheet_revision") or not util.version_gte("saas~18.3"):
            self.skipTest("Spreadsheet fixedPeriod test is skipped for source versions < saas~18.3")

        add_command = {
            "type": "ADD_GLOBAL_FILTER",
            "filter": {
                "id": "42",
                "type": "date",
                "rangeType": "fixedPeriod",
                "label": "my filter",
                "disabledPeriods": ["quarter", "month"],
                "defaultValue": {
                    "yearOffset": -2,
                },
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
                    "res_id": 49,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_commands),
                    "parent_revision_id": False,
                    "revision_uuid": "abcdefghijklmnop",
                },
            ]
        )

        return revision.id

    def check(self, revision_id):
        revision = self.env["spreadsheet.revision"].browse(revision_id)

        commands = json.loads(revision.commands)["commands"]
        add_command, edit_command = commands

        self.assertFalse("defaultValue" in add_command["filter"])
        self.assertFalse("defaultValue" in edit_command["filter"])
        self.assertFalse("rangeType" in add_command["filter"])
        self.assertFalse("rangeType" in edit_command["filter"])
        self.assertFalse("disabledPeriods" in add_command["filter"])
        self.assertFalse("disabledPeriods" in edit_command["filter"])
