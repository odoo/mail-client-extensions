from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.addons.base.maintenance.migrations.util import json


@change_version("saas~18.1")
class TestAddDatasetToOdooChart(UpgradeCase):
    def prepare(self):
        if not util.table_exists(self.env.cr, "spreadsheet_revision"):
            return None

        commands = {
            "type": "REMOTE_REVISION",
            "commands": [
                {
                    "type": "CREATE_CHART",
                    "id": "uuid",
                    "definition": {
                        "type": "odoo_line",
                    },
                },
                {
                    "type": "UPDATE_CHART",
                    "id": "uuid",
                    "definition": {
                        "type": "odoo_bar",
                        "trend": {"type": "exponential"},
                    },
                },
            ],
        }
        field_name = "revision_uuid" if util.version_gte("saas~17.2") else "revision_id"
        revision_id = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 40002,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(commands),
                    field_name: "B",
                    "parent_revision_id": False if util.version_gte("saas~17.2") else "START_REVISION",
                },
            ]
        )
        return revision_id.id

    def check(self, revision_id):
        if not revision_id:
            return
        revisions = self.env["spreadsheet.revision"].browse(revision_id)
        # check the datasets were added to the odoo charts
        commands = json.loads(revisions[0].commands)["commands"]
        self.assertEqual(commands[0]["definition"]["dataSets"], [])
        self.assertEqual(commands[1]["definition"]["dataSets"], [{"trend": {"type": "exponential"}}])
