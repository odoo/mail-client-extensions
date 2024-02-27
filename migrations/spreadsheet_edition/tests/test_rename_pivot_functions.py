# -*- coding: utf-8 -*-

import json

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("17.3")
class TestSpreadsheetRenamePivotFunctions(UpgradeCase):
    def prepare(self):
        if not util.table_exists(self.env.cr, "spreadsheet_revision"):
            return None
        commands = {
            "type": "REMOTE_REVISION",
            "commands": [
                {
                    "type": "UPDATE_CELL",
                    "content": "=ODOO.PIVOT(1)+ODOO.PIVOT.TABLE(1)+ODOO.PIVOT.HEADER(1)",
                },
            ],
        }
        field_name = "revision_uuid" if util.version_gte("saas~17.2") else "revision_id"
        revision_id = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 10000,
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
        self.assertEqual(
            data,
            {
                "type": "REMOTE_REVISION",
                "commands": [
                    {
                        "type": "UPDATE_CELL",
                        "content": "=PIVOT.VALUE(1)+PIVOT(1)+PIVOT.HEADER(1)",
                    },
                ],
            },
        )
