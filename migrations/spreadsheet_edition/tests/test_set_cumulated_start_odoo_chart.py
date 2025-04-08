from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.addons.base.maintenance.migrations.util import json


@change_version("saas~18.4")
class TestSpreadsheetCumulatedStartOdooChart(UpgradeCase):
    def prepare(self):
        if not util.table_exists(self.env.cr, "spreadsheet_revision"):
            return None
        commands = {
            "type": "REMOTE_REVISION",
            "commands": [
                {
                    "sheetId": "sheet1",
                    "id": "fig1",
                    "position": {"x": 10, "y": 10},
                    "definition": {
                        "metaData": {
                            "groupBy": ["stage_id", "user_id"],
                            "measure": "__count",
                            "order": None,
                            "resModel": "crm.lead",
                        },
                        "searchParams": {
                            "context": {"default_type": "opportunity"},
                            "domain": "[]",
                            "groupBy": [],
                            "orderBy": [],
                        },
                        "stacked": True,
                        "fillArea": False,
                        "cumulative": False,
                        "title": {"text": "Opportunities"},
                        "background": "#FFFFFF",
                        "type": "odoo_bar",
                        "dataSourceId": "ds1",
                        "id": "fig1",
                    },
                    "type": "CREATE_CHART",
                },
                {
                    "sheetId": "sheet1",
                    "id": "fig2",
                    "position": {"x": 10, "y": 10},
                    "definition": {
                        "metaData": {
                            "groupBy": ["stage_id", "user_id"],
                            "measure": "__count",
                            "order": None,
                            "resModel": "crm.lead",
                        },
                        "searchParams": {
                            "context": {"default_type": "opportunity"},
                            "domain": "[]",
                            "groupBy": [],
                            "orderBy": [],
                        },
                        "stacked": True,
                        "fillArea": False,
                        "title": {"text": "Opportunities"},
                        "background": "#FFFFFF",
                        "type": "odoo_bar",
                        "dataSourceId": "ds2",
                        "id": "fig2",
                    },
                    "type": "CREATE_CHART",
                },
                {
                    "sheetId": "sheet1",
                    "id": "fig4",
                    "position": {"x": 10, "y": 10},
                    "definition": {
                        "metaData": {
                            "groupBy": ["stage_id", "user_id"],
                            "measure": "__count",
                            "order": None,
                            "resModel": "crm.lead",
                        },
                        "searchParams": {
                            "context": {"default_type": "opportunity"},
                            "domain": "[]",
                            "groupBy": [],
                            "orderBy": [],
                        },
                        "stacked": True,
                        "fillArea": False,
                        "cumulative": True,
                        "cumulatedStart": False,
                        "title": {"text": "Opportunities"},
                        "background": "#FFFFFF",
                        "type": "odoo_bar",
                        "dataSourceId": "ds2",
                        "id": "fig4",
                    },
                    "type": "CREATE_CHART",
                },
                {
                    "sheetId": "sheet1",
                    "id": "fig3",
                    "position": {"x": 10, "y": 10},
                    "definition": {
                        "metaData": {
                            "groupBy": ["stage_id", "user_id"],
                            "measure": "__count",
                            "order": None,
                            "resModel": "crm.lead",
                        },
                        "searchParams": {
                            "context": {"default_type": "opportunity"},
                            "domain": "[]",
                            "groupBy": [],
                            "orderBy": [],
                        },
                        "stacked": True,
                        "fillArea": False,
                        "cumulative": True,
                        "cumulatedStart": True,
                        "title": {"text": "Opportunities"},
                        "background": "#FFFFFF",
                        "type": "odoo_bar",
                        "dataSourceId": "ds2",
                        "id": "fig3",
                    },
                    "type": "CREATE_CHART",
                },
                {
                    "sheetId": "sheet1",
                    "id": "fig1",
                    "definition": {
                        "metaData": {
                            "groupBy": ["stage_id", "user_id"],
                            "measure": "__count",
                            "order": None,
                            "resModel": "crm.lead",
                        },
                        "searchParams": {
                            "context": {"default_type": "opportunity"},
                            "domain": "[]",
                            "groupBy": [],
                            "orderBy": [],
                        },
                        "stacked": True,
                        "fillArea": False,
                        "cumulative": True,
                        "title": {"text": "Opportunities"},
                        "background": "#FFFFFF",
                        "type": "odoo_bar",
                        "dataSourceId": "ds1",
                        "id": "fig1",
                    },
                    "type": "UPDATE_CHART",
                },
            ],
        }
        field_name = "revision_uuid" if util.version_gte("saas~17.2") else "revision_id"
        revision_id = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 40001,
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
        self.assertEqual(data["commands"][0]["definition"]["cumulatedStart"], False)
        self.assertEqual(data["commands"][0]["definition"]["metaData"]["cumulatedStart"], False)
        self.assertEqual(data["commands"][1]["definition"]["cumulatedStart"], False)
        self.assertEqual(data["commands"][1]["definition"]["metaData"]["cumulatedStart"], False)
        self.assertEqual(data["commands"][2]["definition"]["cumulatedStart"], False)
        self.assertEqual(data["commands"][2]["definition"]["metaData"]["cumulatedStart"], False)
        self.assertEqual(data["commands"][3]["definition"]["cumulatedStart"], True)
        self.assertEqual(data["commands"][3]["definition"]["metaData"]["cumulatedStart"], True)
        self.assertEqual(data["commands"][4]["definition"]["cumulatedStart"], True)
        self.assertEqual(data["commands"][4]["definition"]["metaData"]["cumulatedStart"], True)
