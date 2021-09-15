# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.upgrade import util


@change_version("14.5")
class TestSpreadsheetCommandsRename(UpgradeCase):
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
        global_filter = {"id": "A", "fields": {"1": {"field": "date_closed", "type": "datetime"}}, "label": "a filter"}
        commands = {
            "type": "REMOTE_REVISION",
            "commands": [
                {"type": "UPDATE_CELL", "sheetId": "Sheet1", "col": 3, "row": 7, "content": "ADD_PIVOT_FILTER"},
                {"type": "ADD_PIVOT_FILTER", "id": "A", "filter": global_filter},
                {"type": "EDIT_PIVOT_FILTER", "id": "A", "filter": global_filter},
                {"type": "REMOVE_PIVOT_FILTER", "id": "A"},
            ],
        }
        revision = self.env["spreadsheet.revision"].create(
            [
                {
                    "document_id": document.id,
                    "commands": json.dumps(commands),
                    "parent_revision_id": "A",
                    "revision_id": "B",
                },
            ]
        )
        return revision.id

    def check(self, revision_id):
        if not revision_id:
            return
        revision = self.env["spreadsheet.revision"].browse(revision_id)
        global_filter = {
            "id": "A",
            "pivotFields": {"1": {"field": "date_closed", "type": "datetime"}},
            "label": "a filter",
        }
        self.assertEqual(
            json.loads(revision.commands),
            {
                "type": "REMOTE_REVISION",
                "commands": [
                    {"type": "UPDATE_CELL", "sheetId": "Sheet1", "col": 3, "row": 7, "content": "ADD_PIVOT_FILTER"},
                    {"type": "ADD_GLOBAL_FILTER", "id": "A", "filter": global_filter},
                    {"type": "EDIT_GLOBAL_FILTER", "id": "A", "filter": global_filter},
                    {"type": "REMOVE_GLOBAL_FILTER", "id": "A"},
                ],
            },
        )
