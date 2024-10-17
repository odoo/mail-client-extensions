import json

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("15.4")
class TestSpreadsheetAddPivot(UpgradeCase):
    def prepare(self):
        if not util.table_exists(self.env.cr, "spreadsheet_revision"):
            return None
        folder = self.env["documents.folder"].create(
            {
                "name": "folder",
            }
        )
        document = self.env["documents.document"].create(
            {
                "folder_id": folder.id,
            }
        )
        pivot = {
            "model": "MODEL",
            "colGroupBys": ["A", "B"],
            "rowGroupBys": ["C", "D"],
            "measures": [{"field": "MEASURE", "operator": "sum"}],
            "domain": [["A", "=", "test"]],
            "context": {"context_key": "context_value"},
            "id": "1",
        }
        commands = {
            "type": "REMOTE_REVISION",
            "commands": [
                {"type": "ADD_PIVOT", "pivot": pivot},
                # First row of columns => Field A
                {
                    "type": "ADD_PIVOT_FORMULA",
                    "sheetId": "Sheet1",
                    "col": 1,
                    "row": 0,
                    "formula": "PIVOT.HEADER",
                    "args": ["1", "A", "1"],
                },
                {
                    "type": "ADD_PIVOT_FORMULA",
                    "sheetId": "Sheet1",
                    "col": 2,
                    "row": 0,
                    "formula": "PIVOT.HEADER",
                    "args": ["1", "A", "1"],
                },
                {
                    "type": "ADD_PIVOT_FORMULA",
                    "sheetId": "Sheet1",
                    "col": 3,
                    "row": 0,
                    "formula": "PIVOT.HEADER",
                    "args": ["1", "A", "2"],
                },
                {
                    "type": "ADD_PIVOT_FORMULA",
                    "sheetId": "Sheet1",
                    "col": 4,
                    "row": 0,
                    "formula": "PIVOT.HEADER",
                    "args": ["1", "A", "2"],
                },
                # Second row of columns => Field B
                {
                    "type": "ADD_PIVOT_FORMULA",
                    "sheetId": "Sheet1",
                    "col": 1,
                    "row": 1,
                    "formula": "PIVOT.HEADER",
                    "args": ["1", "A", "1", "B", "1"],
                },
                {
                    "type": "ADD_PIVOT_FORMULA",
                    "sheetId": "Sheet1",
                    "col": 2,
                    "row": 1,
                    "formula": "PIVOT.HEADER",
                    "args": ["1", "A", "1", "B", "2"],
                },
                {
                    "type": "ADD_PIVOT_FORMULA",
                    "sheetId": "Sheet1",
                    "col": 3,
                    "row": 1,
                    "formula": "PIVOT.HEADER",
                    "args": ["1", "A", "2", "B", "1"],
                },
                {
                    "type": "ADD_PIVOT_FORMULA",
                    "sheetId": "Sheet1",
                    "col": 4,
                    "row": 1,
                    "formula": "PIVOT.HEADER",
                    "args": ["1", "A", "2", "B", "2"],
                },
                {
                    "type": "ADD_PIVOT_FORMULA",
                    "sheetId": "Sheet1",
                    "col": 5,
                    "row": 1,
                    "formula": "PIVOT.HEADER",
                    "args": ["1"],
                },
                # Third row of columns => Measure
                {
                    "type": "ADD_PIVOT_FORMULA",
                    "sheetId": "Sheet1",
                    "col": 1,
                    "row": 2,
                    "formula": "PIVOT.HEADER",
                    "args": ["1", "A", "1", "B", "1", "measure", "MEASURE"],
                },
                {
                    "type": "ADD_PIVOT_FORMULA",
                    "sheetId": "Sheet1",
                    "col": 2,
                    "row": 2,
                    "formula": "PIVOT.HEADER",
                    "args": ["1", "A", "1", "B", "2", "measure", "MEASURE"],
                },
                {
                    "type": "ADD_PIVOT_FORMULA",
                    "sheetId": "Sheet1",
                    "col": 3,
                    "row": 2,
                    "formula": "PIVOT.HEADER",
                    "args": ["1", "A", "2", "B", "1", "measure", "MEASURE"],
                },
                {
                    "type": "ADD_PIVOT_FORMULA",
                    "sheetId": "Sheet1",
                    "col": 4,
                    "row": 2,
                    "formula": "PIVOT.HEADER",
                    "args": ["1", "A", "2", "B", "2", "measure", "MEASURE"],
                },
                {
                    "type": "ADD_PIVOT_FORMULA",
                    "sheetId": "Sheet1",
                    "col": 5,
                    "row": 2,
                    "formula": "PIVOT.HEADER",
                    "args": ["1", "measure", "MEASURE"],
                },
                # Rows
                {
                    "type": "ADD_PIVOT_FORMULA",
                    "sheetId": "Sheet1",
                    "col": 0,
                    "row": 3,
                    "formula": "PIVOT.HEADER",
                    "args": ["1", "C", "1"],
                },
                {
                    "type": "ADD_PIVOT_FORMULA",
                    "sheetId": "Sheet1",
                    "col": 0,
                    "row": 4,
                    "formula": "PIVOT.HEADER",
                    "args": ["1", "C", "1", "D", "1"],
                },
                {
                    "type": "ADD_PIVOT_FORMULA",
                    "sheetId": "Sheet1",
                    "col": 0,
                    "row": 5,
                    "formula": "PIVOT.HEADER",
                    "args": ["1", "C", "2"],
                },
                {
                    "type": "ADD_PIVOT_FORMULA",
                    "sheetId": "Sheet1",
                    "col": 0,
                    "row": 6,
                    "formula": "PIVOT.HEADER",
                    "args": ["1", "C", "2", "D", "1"],
                },
                {
                    "type": "ADD_PIVOT_FORMULA",
                    "sheetId": "Sheet1",
                    "col": 0,
                    "row": 7,
                    "formula": "PIVOT.HEADER",
                    "args": ["1"],
                },
                # Body (should be ignore)
                {
                    "type": "ADD_PIVOT_FORMULA",
                    "sheetId": "Sheet1",
                    "col": 5,
                    "row": 7,
                    "formula": "PIVOT",
                    "args": ["1", "MEASURE"],
                },
            ],
        }
        revision_insert = self.env["spreadsheet.revision"].create(
            [
                {
                    "document_id": document.id,
                    "commands": json.dumps(commands),
                    "parent_revision_id": "A",
                    "revision_id": "B",
                },
            ]
        )
        commands["commands"].pop(0)
        revision_re_insert = self.env["spreadsheet.revision"].create(
            [
                {
                    "document_id": document.id,
                    "commands": json.dumps(commands),
                    "parent_revision_id": "B",
                    "revision_id": "C",
                },
            ]
        )
        return [revision_insert.id, revision_re_insert.id]

    def check(self, revision_ids):
        if not revision_ids:
            return
        revisions = self.env["spreadsheet.revision"].browse(revision_ids)
        table = {
            "cols": [
                [{"fields": ["A"], "values": ["1"], "width": 2}, {"fields": ["A"], "values": ["2"], "width": 2}],
                [
                    {"fields": ["A", "B"], "values": ["1", "1"], "width": 1},
                    {"fields": ["A", "B"], "values": ["1", "2"], "width": 1},
                    {"fields": ["A", "B"], "values": ["2", "1"], "width": 1},
                    {"fields": ["A", "B"], "values": ["2", "2"], "width": 1},
                    {"fields": [], "values": [], "width": 1},
                ],
                [
                    {"fields": ["A", "B", "measure"], "values": ["1", "1", "MEASURE"], "width": 1},
                    {"fields": ["A", "B", "measure"], "values": ["1", "2", "MEASURE"], "width": 1},
                    {"fields": ["A", "B", "measure"], "values": ["2", "1", "MEASURE"], "width": 1},
                    {"fields": ["A", "B", "measure"], "values": ["2", "2", "MEASURE"], "width": 1},
                    {"fields": ["measure"], "values": ["MEASURE"], "width": 1},
                ],
            ],
            "rows": [
                {"fields": ["C"], "values": ["1"], "indent": 1},
                {"fields": ["C", "D"], "values": ["1", "1"], "indent": 2},
                {"fields": ["C"], "values": ["2"], "indent": 1},
                {"fields": ["C", "D"], "values": ["2", "1"], "indent": 2},
                {"fields": [], "values": [], "indent": 0},
            ],
            "measures": ["MEASURE"],
        }
        definition = {
            "metaData": {
                "colGroupBys": ["A", "B"],
                "rowGroupBys": ["C", "D"],
                "activeMeasures": ["MEASURE"],
                "resModel": "MODEL",
            },
            "searchParams": {
                "comparision": None,
                "context": {"context_key": "context_value"},
                "domain": [["A", "=", "test"]],
                "groupBy": [],
                "orderBy": [],
            },
            "name": "MODEL",
        }
        data = json.loads(revisions[0].commands)
        self.assertEqual(
            data,
            {
                "type": "REMOTE_REVISION",
                "commands": [
                    {
                        "type": "INSERT_PIVOT",
                        "sheetId": "Sheet1",
                        "col": 0,
                        "row": 0,
                        "table": table,
                        "id": "1",
                        "dataSourceId": data["commands"][0]["dataSourceId"],
                        "definition": definition,
                    }
                ],
            },
        )
        self.assertEqual(
            json.loads(revisions[1].commands),
            {
                "type": "REMOTE_REVISION",
                "commands": [
                    {
                        "type": "RE_INSERT_PIVOT",
                        "sheetId": "Sheet1",
                        "col": 0,
                        "row": 0,
                        "table": table,
                        "id": "1",
                    }
                ],
            },
        )
