from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.addons.base.maintenance.migrations.util import json


@change_version("saas~18.4")
class TestRenameCfDv(UpgradeCase):
    def prepare(self):
        if not util.table_exists(self.env.cr, "spreadsheet_revision") or not util.version_gte("saas~18.3"):
            return None

        commands = {
            "type": "REMOTE_REVISION",
            "commands": [
                {
                    "sheetId": "sh1",
                    "ranges": [{"_sheetId": "sh1", "_zone": {"top": 0, "left": 0, "bottom": 0, "right": 0}}],
                    "rule": {"id": "7612071e-4755", "criterion": {"type": "textContains", "values": ["text"]}},
                    "type": "ADD_DATA_VALIDATION_RULE",
                },
                {
                    "sheetId": "sh1",
                    "ranges": [{"_sheetId": "sh1", "_zone": {"left": 0, "right": 0, "top": 5, "bottom": 5}}],
                    "cf": {
                        "id": "ac1f8cd7-f134",
                        "rule": {
                            "type": "CellIsRule",
                            "operator": "Between",
                            "style": {"fillColor": "#b6d7a8"},
                            "values": [],
                        },
                    },
                    "type": "ADD_CONDITIONAL_FORMAT",
                },
            ],
        }

        revision_id = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 40020,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(commands),
                    "revision_uuid": "B",
                    "parent_revision_id": False,
                },
            ]
        )
        return revision_id.id

    def check(self, revision_id):
        if not revision_id:
            return
        revisions = self.env["spreadsheet.revision"].browse(revision_id)
        commands = json.loads(revisions[0].commands)["commands"]

        converted_data_validation_type = commands[0]["rule"]["criterion"]["type"]
        self.assertEqual(converted_data_validation_type, "containsText")

        converted_conditional_format_operator = commands[1]["cf"]["rule"]["operator"]
        self.assertEqual(converted_conditional_format_operator, "isBetween")
