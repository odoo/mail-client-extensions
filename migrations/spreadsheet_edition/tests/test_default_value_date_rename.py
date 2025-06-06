from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.addons.base.maintenance.migrations.util import json


@change_version("saas~18.4")
class TestDefaultValueDateRename(UpgradeCase):
    def prepare(self):
        if not util.table_exists(self.env.cr, "spreadsheet_revision") or not util.version_gte("saas~18.3"):
            self.skipTest("Spreadsheet fixedPeriod test is skipped for source versions < saas~18.3")

        add_commands = [
            {
                "type": "ADD_GLOBAL_FILTER",
                "filter": {
                    "id": "42",
                    "type": "date",
                    "rangeType": "relative",
                    "label": "my filter",
                    "defaultValue": default_value,
                },
            }
            for default_value in (
                "last_six_month",
                "last_three_years",
                "last_week",
                "last_month",
                "last_three_months",
                "last_year",
            )
        ]

        edit_commands = [
            {
                "filter": add_command["filter"],
                "type": "EDIT_GLOBAL_FILTER",
            }
            for add_command in add_commands
        ]

        revision_commands = {
            "type": "REMOTE_REVISION",
            "commands": add_commands + edit_commands,
        }

        revision = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 50,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(revision_commands),
                    "parent_revision_id": False,
                    "revision_uuid": "abcdefghijklmnopq",
                },
            ]
        )

        return revision.id

    def check(self, revision_id):
        revision = self.env["spreadsheet.revision"].browse(revision_id)

        commands = json.loads(revision.commands)["commands"]
        add_commands, edit_commands = commands[:6], commands[6:]

        self.assertFalse("defaultValue" in add_commands[0]["filter"])  # last_six_month is removed
        self.assertFalse("defaultValue" in add_commands[1]["filter"])  # last_three_years is removed
        self.assertEqual(add_commands[2]["filter"]["defaultValue"], "last_7_days")  # last_week is renamed
        self.assertEqual(add_commands[3]["filter"]["defaultValue"], "last_30_days")  # last_month is renamed
        self.assertEqual(add_commands[4]["filter"]["defaultValue"], "last_90_days")  # last_three_months is renamed
        self.assertEqual(add_commands[5]["filter"]["defaultValue"], "last_12_months")  # last_year is renamed

        self.assertFalse("defaultValue" in edit_commands[0]["filter"])  # last_six_month is removed
        self.assertFalse("defaultValue" in edit_commands[1]["filter"])  # last_three_years is removed
        self.assertEqual(edit_commands[2]["filter"]["defaultValue"], "last_7_days")  # last_week is renamed
        self.assertEqual(edit_commands[3]["filter"]["defaultValue"], "last_30_days")  # last_month is renamed
        self.assertEqual(edit_commands[4]["filter"]["defaultValue"], "last_90_days")  # last_three_months is renamed
        self.assertEqual(edit_commands[5]["filter"]["defaultValue"], "last_12_months")  # last_year is renamed
