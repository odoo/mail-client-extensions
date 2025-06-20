from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.addons.base.maintenance.migrations.util import json


@change_version("saas~18.1")
class TestPivotSortedColumn(UpgradeCase):
    def prepare(self):
        if not util.table_exists(self.env.cr, "spreadsheet_revision"):
            return None

        pivot1 = {
            "type": "ODOO",
            "rows": [],
            "columns": [],
            "measures": [{"id": "MEASURE:sum", "fieldName": "MEASURE", "aggregator": "sum"}],
            "model": "MODEL",
            "name": "MODEL",
            "sortedColumn": {
                "order": "asc",
                "measure": "MEASURE",
                "groupId": [[], []],
            },
        }
        pivot2 = {
            **pivot1,
            "sortedColumn": {
                "order": "asc",
                "measure": "MEASURE",
                "groupId": [[], [5]],
            },
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

        field_name = "revision_uuid" if util.version_gte("saas~17.2") else "revision_id"
        revision_id = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 40009,
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
        self.assertEqual(
            commands[0]["pivot"]["sortedColumn"],
            {
                "order": "asc",
                "measure": "MEASURE:sum",
                "domain": [],
            },
        )
        self.assertEqual(
            commands[1]["pivot"]["sortedColumn"],
            {
                "order": "asc",
                "measure": "MEASURE:sum",
                "domain": [],
            },
        )
        self.assertEqual(commands[2]["pivot"].get("sortedColumn"), None)
        self.assertEqual(commands[3]["pivot"].get("sortedColumn"), None)


@change_version("saas~18.4")
class TestCleanPivotSortedColumn(UpgradeCase):
    def prepare(self):
        if not util.version_gte("saas~18.3"):
            self.skipTest("sorted column cleaning test is skipped for versions < saas~18.3")

        pivot1 = {
            "type": "ODOO",
            "rows": [],
            "columns": [],
            "measures": [{"id": "MEASURE:sum", "fieldName": "MEASURE", "aggregator": "sum"}],
            "model": "MODEL",
            "name": "MODEL",
            "sortedColumn": {
                "order": "asc",
                "measure": "MEASURE",  # not correct, should be "MEASURE:sum"
                "domain": [],
            },
        }
        pivot2 = {
            **pivot1,
            "sortedColumn": {
                "order": "asc",
                "measure": "MEASURE:sum",  # correct
                "domain": [],
            },
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
                    "res_id": 40009,
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
        self.assertEqual(
            commands[0]["pivot"]["sortedColumn"]["measure"],
            "MEASURE:sum",
        )
        self.assertEqual(
            commands[1]["pivot"]["sortedColumn"]["measure"],
            "MEASURE:sum",
        )
        self.assertEqual(
            commands[2]["pivot"]["sortedColumn"]["measure"],
            "MEASURE:sum",
        )
        self.assertEqual(
            commands[3]["pivot"]["sortedColumn"]["measure"],
            "MEASURE:sum",
        )
