# -*- coding: utf-8 -*-

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
                "colGroupBys": ["A", "B"],
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
            "colGroupBys": ["A", "B"],
            "rowGroupBys": ["C", "D"],
            "measures": ["MEASURE"],
            "model": "MODEL",
            "context": {"context_key": "context_value"},
            "domain": [["A", "=", "test"]],
            "name": "MODEL",
            "sortedColumn": None,
        }
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
