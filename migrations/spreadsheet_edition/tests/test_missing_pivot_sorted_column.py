from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.addons.base.maintenance.migrations.util import json


@change_version("saas~18.3")
class TestPivotMissingSortedColumn(UpgradeCase):
    def prepare(self):
        if not util.table_exists(self.env.cr, "spreadsheet_revision") or not util.version_gte("saas~18.2"):
            return None

        pivot1 = {
            "type": "ODOO",
            "rows": [],
            "columns": [],
            "measures": [],
            "model": "MODEL",
            "name": "MODEL",
            "sortedColumn": {
                "order": "asc",
                "measure": "measure:sum",
                "domain": [],
            },
        }
        pivot2 = {
            **pivot1,
            # same with the measure
            "measures": [{"id": "measure:sum", "fieldName": "MEASURE", "aggregator": "sum"}],
        }
        commands = {
            "type": "REMOTE_REVISION",
            "commands": [
                {
                    "type": "ADD_PIVOT",
                    "pivot": pivot1,
                    "pivotId": "1",
                },
                {
                    "type": "UPDATE_PIVOT",
                    "pivot": pivot1,
                    "pivotId": "1",
                },
                {
                    "type": "ADD_PIVOT",
                    "pivot": pivot2,
                    "pivotId": "2",
                },
                {
                    "type": "UPDATE_PIVOT",
                    "pivot": pivot2,
                    "pivotId": "2",
                },
            ],
        }

        revision_id = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 40019,
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
        self.assertEqual(commands[0]["pivot"].get("sortedColumn"), None)
        self.assertEqual(commands[1]["pivot"].get("sortedColumn"), None)

        # unchanged
        self.assertEqual(
            commands[2]["pivot"]["sortedColumn"],
            {
                "order": "asc",
                "measure": "measure:sum",
                "domain": [],
            },
        )
        self.assertEqual(
            commands[3]["pivot"]["sortedColumn"],
            {
                "order": "asc",
                "measure": "measure:sum",
                "domain": [],
            },
        )
