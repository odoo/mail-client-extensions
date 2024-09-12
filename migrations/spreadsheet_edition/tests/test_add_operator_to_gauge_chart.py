import json

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.5")
class TestSpreadsheetAddOperatorToGaugeChart(UpgradeCase):
    def prepare(self):
        if not util.table_exists(self.env.cr, "spreadsheet_revision"):
            return None

        commands = {
            "type": "REMOTE_REVISION",
            "commands": [
                {
                    "type": "CREATE_CHART",
                    "definition": {
                        "type": "gauge",
                        "sectionRule": {
                            "lowerInflectionPoint": {"type": "percentage", "value": "15"},
                            "upperInflectionPoint": {"type": "percentage", "value": "40"},
                        },
                    },
                },
                {
                    "type": "UPDATE_CHART",
                    "definition": {
                        "type": "gauge",
                        "sectionRule": {
                            "lowerInflectionPoint": {"type": "percentage", "value": "15"},
                            "upperInflectionPoint": {"type": "percentage", "value": "40"},
                        },
                    },
                },
            ],
        }
        field_name = "revision_uuid" if util.version_gte("saas~17.2") else "revision_id"
        revision_id = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 40001,
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
        # check the operator "<=" was added to the sectionRules
        data = json.loads(revisions[0].commands)
        for command in data["commands"]:
            self.assertEqual(command["definition"]["sectionRule"]["lowerInflectionPoint"]["operator"], "<=")
            self.assertEqual(command["definition"]["sectionRule"]["upperInflectionPoint"]["operator"], "<=")
