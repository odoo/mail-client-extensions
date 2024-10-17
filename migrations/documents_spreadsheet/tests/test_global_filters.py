import json

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("16.0")
class TestSpreadsheetGlobalFilters(UpgradeCase):
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

        relation_command = {
            "type": "ADD_GLOBAL_FILTER",
            "id": "xx",
            "filter": {
                "id": "xx",
                "type": "relation",
                "label": "Companies",
                "modelName": "res.company",
                "defaultValue": [1],
                "defaultValueDisplayNames": ["YourCompany"],
                "rangeType": "year",
                "pivotFields": {"1": {"field": "company_id", "type": "many2one"}},
                "listFields": {"1": {"field": "company_id", "type": "many2one"}},
            },
        }
        text_command = {
            "type": "ADD_GLOBAL_FILTER",
            "id": "tt",
            "filter": {
                "id": "tt",
                "type": "text",
                "label": "text filter",
                "defaultValue": "tabouret",
                "rangeType": "year",
                "pivotFields": {"1": {"field": "company_id", "type": "many2one"}},
                "listFields": {"1": {"field": "company_id", "type": "many2one"}},
            },
        }
        year_command = {
            "type": "ADD_GLOBAL_FILTER",
            "id": "12",
            "filter": {
                "id": "12",
                "type": "date",
                "label": "Year filter",
                "defaultValue": {"year": "last_year"},
                "rangeType": "year",
                "pivotFields": {"1": {"field": "date", "type": "date"}},
                "listFields": {"1": {"field": "date", "type": "date"}},
            },
        }

        quarter_command = {
            "type": "ADD_GLOBAL_FILTER",
            "id": "13",
            "filter": {
                "id": "13",
                "type": "date",
                "label": "Quarter filter",
                "defaultValue": {"year": "this_year", "period": "third_quarter"},
                "rangeType": "quarter",
                "pivotFields": {"1": {"field": "date", "type": "date"}},
                "listFields": {"1": {"field": "date", "type": "date"}},
            },
        }

        month_command = {
            "type": "ADD_GLOBAL_FILTER",
            "id": "14",
            "filter": {
                "id": "14",
                "type": "date",
                "label": "Month filter",
                "defaultValue": {"year": "antepenultimate_year", "period": "may"},
                "rangeType": "month",
                "pivotFields": {"1": {"field": "date", "type": "date"}},
                "listFields": {"1": {"field": "date", "type": "date"}},
            },
        }

        remove_command = {
            "type": "REMOVE_GLOBAL_FILTER",
            "id": "27",
        }

        revision_commands = {
            "type": "REMOTE_REVISION",
            "commands": [
                relation_command,
                text_command,
                year_command,
                quarter_command,
                month_command,
                remove_command,
            ],
        }

        revisions_insert = self.env["spreadsheet.revision"].create(
            [
                {
                    "document_id": document.id,
                    "commands": json.dumps(revision_commands),
                    "parent_revision_id": "A",
                    "revision_id": "B",
                },
            ]
        )

        return revisions_insert.id

    def check(self, revision_id):
        if not revision_id:
            return
        revision = self.env["spreadsheet.revision"].browse(revision_id)

        def _get_filter(command):
            if command["type"] == "REMOVE_GLOBAL_FILTER" or "_GLOBAL_FILTER" not in command["type"]:
                return None
            return command.get("filter", {})

        def _get_filter_default(command):
            return _get_filter(command).get("defaultValue", None)

        commands = json.loads(revision.commands)["commands"]
        self.assertEqual(len(commands), 6, "There should be 6 commands in the revision")

        self.assertEqual(
            _get_filter_default(commands[0]),
            [1],
        )

        self.assertEqual(
            _get_filter_default(commands[1]),
            "tabouret",
        )

        self.assertEqual(
            _get_filter_default(commands[2]),
            {"yearOffset": -1},
        )

        self.assertEqual(
            _get_filter_default(commands[3]),
            {"yearOffset": 0, "period": "third_quarter"},
        )

        self.assertEqual(
            _get_filter_default(commands[4]),
            {"yearOffset": -2, "period": "may"},
        )

        self.assertEqual(
            _get_filter(commands[5]),
            None,
        )
