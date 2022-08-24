# -*- coding: utf-8 -*-

import json

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("15.4")
class TestSpreadsheetAddList(UpgradeCase):
    def prepare(self):
        if not util.table_exists(self.env.cr, "spreadsheet_revision"):
            return
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
        list = {
            "model": "MODEL",
            "domain": [["A", "=", "test"]],
            "context": {"context_key": "context_value"},
            "orderBy": [],
            "columns": ["A", "B"],
            "id": "1",
        }
        commands = {
            "type": "REMOTE_REVISION",
            "commands": [
                {"type": "ADD_ODOO_LIST", "list": list},
                # Headers of list
                {
                    "type": "ADD_ODOO_LIST_FORMULA",
                    "sheetId": "Sheet1",
                    "col": 0,
                    "row": 0,
                    "formula": "LIST.HEADER",
                    "args": ["1", "A"],
                },
                {
                    "type": "ADD_ODOO_LIST_FORMULA",
                    "sheetId": "Sheet1",
                    "col": 1,
                    "row": 0,
                    "formula": "LIST.HEADER",
                    "args": ["1", "B"],
                },
                # Rows (lines Number = 2)
                {
                    "type": "ADD_ODOO_LIST_FORMULA",
                    "sheetId": "Sheet1",
                    "col": 0,
                    "row": 1,
                    "formula": "LIST",
                    "args": ["1", "1", "A"],
                },
                {
                    "type": "ADD_ODOO_LIST_FORMULA",
                    "sheetId": "Sheet1",
                    "col": 1,
                    "row": 1,
                    "formula": "LIST",
                    "args": ["1", "1", "B"],
                },
                {
                    "type": "ADD_ODOO_LIST_FORMULA",
                    "sheetId": "Sheet1",
                    "col": 0,
                    "row": 2,
                    "formula": "LIST",
                    "args": ["1", "2", "A"],
                },
                {
                    "type": "ADD_ODOO_LIST_FORMULA",
                    "sheetId": "Sheet1",
                    "col": 1,
                    "row": 2,
                    "formula": "LIST",
                    "args": ["1", "2", "B"],
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
        definition = {
            "metaData": {
                "resModel": "MODEL",
                "columns": ["A", "B"],
            },
            "searchParams": {
                "context": {"context_key": "context_value"},
                "domain": [["A", "=", "test"]],
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
                        "type": "INSERT_ODOO_LIST",
                        "sheetId": "Sheet1",
                        "col": 0,
                        "row": 0,
                        "id": "1",
                        "dataSourceId": data["commands"][0]["dataSourceId"],
                        "definition": definition,
                        "linesNumber": 2,
                        "columns": [{"name": "A", "type": ""}, {"name": "B", "type": ""}],
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
                        "type": "RE_INSERT_ODOO_LIST",
                        "sheetId": "Sheet1",
                        "col": 0,
                        "row": 0,
                        "id": "1",
                        "linesNumber": 2,
                        "columns": [{"name": "A", "type": ""}, {"name": "B", "type": ""}],
                    }
                ],
            },
        )
