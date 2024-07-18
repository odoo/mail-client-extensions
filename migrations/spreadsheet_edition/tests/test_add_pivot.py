import json

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("17.3")
class TestSpreadsheetInsertPivot(UpgradeCase):
    def prepare(self):
        if not util.table_exists(self.env.cr, "spreadsheet_revision"):
            return None
        pivot = {
            "type": "ODOO",
            "colGroupBys": ["A", "B"],
            "rowGroupBys": ["C", "D"],
            "measures": ["MEASURE"],
            "model": "MODEL",
            "context": {"context_key": "context_value"},
            "domain": [["A", "=", "test"]],
            "name": "MODEL",
            "sortedColumn": None,
        }
        commands = {
            "type": "REMOTE_REVISION",
            "commands": [
                {
                    "type": "ADD_PIVOT",
                    "pivot": pivot,
                    "pivotId": "1",
                },
                {
                    "type": "UPDATE_PIVOT",
                    "pivot": pivot,
                    "pivotId": "1",
                },
            ],
        }
        field_name = "revision_uuid" if util.version_gte("saas~17.2") else "revision_id"
        revision_id = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 1000,
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

        data = json.loads(revisions[0].commands)
        pivot = data["commands"][0]["pivot"]

        for cmd in data["commands"]:
            pivot = cmd["pivot"]

            if util.version_gte("saas~17.5"):
                self.assertEqual(pivot["measures"], [{"fieldName": "MEASURE", "id": "MEASURE"}])
                self.assertEqual(pivot["columns"], [{"fieldName": "A", "id": "A"}, {"fieldName": "B", "id": "B"}])
                self.assertEqual(pivot["rows"], [{"fieldName": "C", "id": "C"}, {"fieldName": "D", "id": "D"}])
            else:
                self.assertEqual(pivot["measures"], [{"name": "MEASURE"}])
                self.assertEqual(pivot["columns"], [{"name": "A"}, {"name": "B"}])
                self.assertEqual(pivot["rows"], [{"name": "C"}, {"name": "D"}])
