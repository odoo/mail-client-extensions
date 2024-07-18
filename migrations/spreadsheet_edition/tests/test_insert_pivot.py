import json

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("17.2")
class TestSpreadsheetInsertPivot(UpgradeCase):
    def prepare(self):
        if not util.table_exists(self.env.cr, "spreadsheet_revision"):
            return None
        definition = {
            "metaData": {
                "colGroupBys": ["A:month", "B"],
                "rowGroupBys": ["C", "D"],
                "activeMeasures": ["MEASURE"],
                "resModel": "MODEL",
            },
            "searchParams": {
                "context": {"context_key": "context_value"},
                "domain": [["A", "=", "test"]],
            },
            "name": "MODEL",
        }
        commands = {
            "type": "REMOTE_REVISION",
            "commands": [
                {
                    "type": "INSERT_PIVOT",
                    "sheetId": "Sheet1",
                    "col": 0,
                    "row": 0,
                    "table": {
                        "cols": [],
                    },
                    "id": "1",
                    "definition": definition,
                },
                {
                    "type": "RE_INSERT_PIVOT",
                    "sheetId": "Sheet1",
                    "col": 5,
                    "row": 5,
                    "table": {
                        "cols": [],
                    },
                    "id": "1",
                },
                {
                    "type": "RENAME_ODOO_PIVOT",
                    "pivotId": "1",
                    "name": "name",
                },
            ],
        }
        revision_insert = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 1,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(commands),
                    "parent_revision_id": "A",
                    "revision_id": "B",
                },
            ]
        )
        return [revision_insert.id]

    def check(self, revision_ids):
        if not revision_ids:
            return
        revisions = self.env["spreadsheet.revision"].browse(revision_ids)

        pivot = {
            "type": "ODOO",
            "colGroupBys": ["A:month", "B"],
            "rowGroupBys": ["C", "D"],
            "measures": ["MEASURE"],
            "model": "MODEL",
            "context": {"context_key": "context_value"},
            "domain": [["A", "=", "test"]],
            "name": "MODEL",
            "sortedColumn": None,
        }

        if util.version_gte("saas~17.3"):
            pivot["columns"] = [{"name": "A", "granularity": "month"}, {"name": "B"}]
            pivot["rows"] = [{"name": "C"}, {"name": "D"}]
            pivot["measures"] = [{"name": "MEASURE"}]
            del pivot["colGroupBys"]
            del pivot["rowGroupBys"]

        if util.version_gte("saas~17.5"):
            pivot["columns"] = [
                {
                    "fieldName": "A",
                    "granularity": "month",
                    "id": "A",
                },
                {"fieldName": "B", "id": "B"},
            ]
            pivot["rows"] = [
                {"fieldName": "C", "id": "C"},
                {
                    "fieldName": "D",
                    "id": "D",
                },
            ]
            pivot["measures"] = [{"fieldName": "MEASURE", "id": "MEASURE"}]

        data = json.loads(revisions[0].commands)
        self.assertEqual(
            data,
            {
                "type": "REMOTE_REVISION",
                "commands": [
                    {
                        "type": "ADD_PIVOT",
                        "pivot": pivot,
                        "pivotId": "1",
                    },
                    {
                        "type": "INSERT_PIVOT",
                        "pivotId": "1",
                        "sheetId": "Sheet1",
                        "col": 0,
                        "row": 0,
                        "table": {
                            "cols": [],
                        },
                    },
                    {
                        "type": "INSERT_PIVOT",
                        "sheetId": "Sheet1",
                        "col": 5,
                        "row": 5,
                        "table": {
                            "cols": [],
                        },
                        "pivotId": "1",
                    },
                    {
                        "type": "RENAME_PIVOT",
                        "pivotId": "1",
                        "name": "name",
                    },
                ],
            },
        )
