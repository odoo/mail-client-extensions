from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.addons.base.maintenance.migrations.util import json


@change_version("17.3")
class TestSpreadsheetRenamePivotFunctions(UpgradeCase):
    def prepare(self):
        if not util.table_exists(self.env.cr, "spreadsheet_revision"):
            return None

        commands = {
            "type": "REMOTE_REVISION",
            "commands": [
                {
                    "type": "CREATE_CHART",
                    "definition": {
                        "type": "line",
                        "title": "Chart Title",
                        "dataSets": ["A1:B2", "C1:D2"],
                    },
                },
                {
                    "type": "UPDATE_CHART",
                    "definition": {
                        "type": "line",
                        "title": "Chart Title",
                        "dataSets": ["C1:D2"],
                    },
                },
                {
                    "type": "CREATE_CHART",
                    "definition": {
                        "type": "bar",
                        "title": "Chart Title",
                        "dataSets": ["A1:B2", "C1:D2"],
                    },
                },
                {
                    "type": "UPDATE_CHART",
                    "definition": {
                        "type": "bar",
                        "title": "Chart Title",
                        "dataSets": ["C1:D2"],
                        "verticalAxisPosition": "right",
                    },
                },
                {
                    "type": "CREATE_CHART",
                    "definition": {
                        "type": "pie",
                        "title": "Chart Title",
                        "dataSets": ["A1:B2", "C1:D2"],
                    },
                },
                {
                    "type": "UPDATE_CHART",
                    "definition": {
                        "type": "pie",
                        "title": "Chart Title",
                        "dataSets": ["C1:D2"],
                    },
                },
                {
                    "type": "CREATE_CHART",
                    "definition": {
                        "type": "scorecard",
                        "title": "Chart Title",
                    },
                },
                {
                    "type": "UPDATE_CHART",
                    "definition": {
                        "type": "scorecard",
                        "title": "Chart Title",
                    },
                },
                {
                    "type": "CREATE_CHART",
                    "definition": {
                        "type": "gauge",
                        "title": "Chart Title",
                    },
                },
                {
                    "type": "UPDATE_CHART",
                    "definition": {
                        "type": "gauge",
                        "title": "Chart Title",
                    },
                },
                {
                    "type": "CREATE_CHART",
                    "definition": {
                        "type": "scatter",
                        "title": "Chart Title",
                        "dataSets": ["A1:B2", "C1:D2"],
                    },
                },
                {
                    "type": "UPDATE_CHART",
                    "definition": {
                        "type": "scatter",
                        "title": "Chart Title",
                        "dataSets": ["C1:D2"],
                    },
                },
                {
                    "type": "CREATE_CHART",
                    "definition": {
                        "type": "combo",
                        "title": "Chart Title",
                    },
                },
                {
                    "type": "UPDATE_CHART",
                    "definition": {
                        "type": "combo",
                        "title": "Chart Title",
                    },
                },
                {
                    "type": "CREATE_CHART",
                    "definition": {
                        "type": "waterfall",
                        "title": "Chart Title",
                        "dataSets": ["A1:B2", "C1:D2"],
                    },
                },
                {
                    "type": "UPDATE_CHART",
                    "definition": {
                        "type": "waterfall",
                        "title": "Chart Title",
                        "dataSets": ["C1:D2"],
                    },
                },
            ],
        }
        field_name = "revision_uuid" if util.version_gte("saas~17.2") else "revision_id"
        revision_id = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 40000,
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
                        "type": "CREATE_CHART",
                        "definition": {
                            "type": "line",
                            "title": {"text": "Chart Title"},
                            "dataSets": [
                                {"dataRange": "A1:B2"},
                                {"dataRange": "C1:D2"},
                            ],
                        },
                    },
                    {
                        "type": "UPDATE_CHART",
                        "definition": {
                            "type": "line",
                            "title": {"text": "Chart Title"},
                            "dataSets": [{"dataRange": "C1:D2"}],
                        },
                    },
                    {
                        "type": "CREATE_CHART",
                        "definition": {
                            "type": "bar",
                            "title": {"text": "Chart Title"},
                            "dataSets": [
                                {"dataRange": "A1:B2"},
                                {"dataRange": "C1:D2"},
                            ],
                        },
                    },
                    {
                        "type": "UPDATE_CHART",
                        "definition": {
                            "type": "bar",
                            "title": {"text": "Chart Title"},
                            "dataSets": [
                                {"dataRange": "C1:D2"},
                            ],
                            "verticalAxisPosition": "right",
                        },
                    },
                    {
                        "type": "CREATE_CHART",
                        "definition": {
                            "type": "pie",
                            "title": {"text": "Chart Title"},
                            "dataSets": [
                                {"dataRange": "A1:B2"},
                                {"dataRange": "C1:D2"},
                            ],
                        },
                    },
                    {
                        "type": "UPDATE_CHART",
                        "definition": {
                            "type": "pie",
                            "title": {"text": "Chart Title"},
                            "dataSets": [
                                {"dataRange": "C1:D2"},
                            ],
                        },
                    },
                    {
                        "type": "CREATE_CHART",
                        "definition": {
                            "type": "scorecard",
                            "title": {"text": "Chart Title"},
                        },
                    },
                    {
                        "type": "UPDATE_CHART",
                        "definition": {
                            "type": "scorecard",
                            "title": {"text": "Chart Title"},
                        },
                    },
                    {
                        "type": "CREATE_CHART",
                        "definition": {
                            "type": "gauge",
                            "title": {"text": "Chart Title"},
                        },
                    },
                    {
                        "type": "UPDATE_CHART",
                        "definition": {
                            "type": "gauge",
                            "title": {"text": "Chart Title"},
                        },
                    },
                    {
                        "type": "CREATE_CHART",
                        "definition": {
                            "type": "scatter",
                            "title": {"text": "Chart Title"},
                            "dataSets": [
                                {"dataRange": "A1:B2"},
                                {"dataRange": "C1:D2"},
                            ],
                        },
                    },
                    {
                        "type": "UPDATE_CHART",
                        "definition": {
                            "type": "scatter",
                            "title": {"text": "Chart Title"},
                            "dataSets": [{"dataRange": "C1:D2"}],
                        },
                    },
                    {
                        "type": "CREATE_CHART",
                        "definition": {
                            "type": "combo",
                            "title": {"text": "Chart Title"},
                        },
                    },
                    {
                        "type": "UPDATE_CHART",
                        "definition": {
                            "type": "combo",
                            "title": {"text": "Chart Title"},
                        },
                    },
                    {
                        "type": "CREATE_CHART",
                        "definition": {
                            "type": "waterfall",
                            "title": {"text": "Chart Title"},
                            "dataSets": [
                                {"dataRange": "A1:B2"},
                                {"dataRange": "C1:D2"},
                            ],
                        },
                    },
                    {
                        "type": "UPDATE_CHART",
                        "definition": {
                            "type": "waterfall",
                            "title": {"text": "Chart Title"},
                            "dataSets": [{"dataRange": "C1:D2"}],
                        },
                    },
                ],
            },
        )


@change_version("saas~18.4")
class TestSpreadsheetScorecardStyle(UpgradeCase):
    def prepare(self):
        if not util.table_exists(self.env.cr, "spreadsheet_revision"):
            return None
        id_field_name = "figureId" if util.version_gte("saas~18.3") else "id"
        position = {"offset": {"x": 0, "y": 0}, "col": 0, "row": 0} if util.version_gte("saas~18.3") else {}

        commands = {
            "type": "REMOTE_REVISION",
            "commands": [
                {
                    "type": "CREATE_CHART",
                    id_field_name: "SCORECARD1",
                    "definition": {
                        "type": "scorecard",
                        "baselineDescr": "Baseline Description",
                        "dataSets": ["A1:B2", "C1:D2"],
                    },
                    **position,
                },
                {
                    "type": "UPDATE_CHART",
                    id_field_name: "SCORECARD1",
                    "definition": {
                        "type": "scorecard",
                        "baselineDescr": "new Baseline Description",
                        "title": "Chart Title",
                        "dataSets": ["C1:D2"],
                    },
                },
                {
                    "type": "CREATE_CHART",
                    id_field_name: "chartId",
                    "definition": {
                        "type": "line",
                        "title": "Chart Title",
                        "dataSets": ["A1:B2", "C1:D2"],
                    },
                    **position,
                },
                {
                    "type": "UPDATE_CHART",
                    id_field_name: "chartId",
                    "definition": {
                        "type": "line",
                        "title": "Chart Title",
                        "dataSets": ["A1:B2", "C1:D2"],
                    },
                },
            ],
        }
        revision_id = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 40000,
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
        data = json.loads(revisions[0].commands)
        self.assertEqual(
            data,
            {
                "type": "REMOTE_REVISION",
                "commands": [
                    {
                        "type": "CREATE_CHART",
                        "definition": {
                            "type": "scorecard",
                            "baselineDescr": {"text": "Baseline Description"},
                            "dataSets": ["A1:B2", "C1:D2"],
                        },
                        "figureId": "SCORECARD1",
                        "offset": {"x": 0, "y": 0},
                        "col": 0,
                        "row": 0,
                    },
                    {
                        "type": "UPDATE_CHART",
                        "definition": {
                            "type": "scorecard",
                            "baselineDescr": {"text": "new Baseline Description"},
                            "title": "Chart Title",
                            "dataSets": ["C1:D2"],
                        },
                        "figureId": "SCORECARD1",
                    },
                    {
                        "type": "CREATE_CHART",
                        "definition": {
                            "type": "line",
                            "title": "Chart Title",
                            "dataSets": ["A1:B2", "C1:D2"],
                        },
                        "figureId": "chartId",
                        "offset": {"x": 0, "y": 0},
                        "col": 0,
                        "row": 0,
                    },
                    {
                        "type": "UPDATE_CHART",
                        "definition": {
                            "type": "line",
                            "title": "Chart Title",
                            "dataSets": ["A1:B2", "C1:D2"],
                        },
                        "figureId": "chartId",
                    },
                ],
            },
        )
