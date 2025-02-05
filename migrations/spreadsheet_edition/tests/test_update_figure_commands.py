from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.addons.base.maintenance.migrations.util import json


@change_version("saas~18.3")
class TestChangePositionFigure(UpgradeCase):
    def prepare(self):
        if not util.table_exists(self.env.cr, "spreadsheet_revision"):
            return None

        commands = {
            "type": "REMOTE_REVISION",
            "commands": [
                {
                    "type": "CREATE_CHART",
                    "position": {"x": 50, "y": 100},
                    "id": "chartId",
                    "definition": {
                        "type": "line",
                        "title": "Chart Title",
                        "dataSets": ["A1:B2", "C1:D2"],
                    },
                },
                {
                    "type": "CREATE_IMAGE",
                    "figureId": "1",
                    "position": {"x": 1, "y": 2},
                    "size": {"width": 100, "height": 100},
                    "definition": {
                        "path": "/web/image/ABC",
                        "size": {"width": 100, "height": 100},
                        "mimetype": "image/png",
                    },
                },
                {
                    "type": "UPDATE_CHART",
                    "id": "chartId",
                    "definition": {
                        "type": "line",
                        "title": "Chart Title",
                        "dataSets": ["A1:B2", "C1:D2"],
                    },
                },
                {
                    "type": "UPDATE_FIGURE",
                    "id": "chartId",
                    "x": 5,
                    "y": 10,
                },
                {
                    "type": "SELECT_FIGURE",
                    "id": "chartId",
                },
                {
                    "type": "DELETE_FIGURE",
                    "id": "chartId",
                },
                {"type": "SET_BORDER", "border": None, "col": 10, "row": 10, "sheetId": "uuid"},
            ],
        }
        field_name = "revision_uuid" if util.version_gte("saas~17.2") else "revision_id"
        revision_id = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 654456,
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
            commands,
            [
                {
                    "type": "CREATE_CHART",
                    "offset": {"x": 50, "y": 100},
                    "col": 0,
                    "row": 0,
                    "figureId": "chartId",
                    "definition": {
                        "type": "line",
                        "title": "Chart Title",
                        "dataSets": ["A1:B2", "C1:D2"],
                    },
                },
                {
                    "type": "CREATE_IMAGE",
                    "figureId": "1",
                    "offset": {"x": 1, "y": 2},
                    "col": 0,
                    "row": 0,
                    "size": {"width": 100, "height": 100},
                    "definition": {
                        "path": "/web/image/ABC",
                        "size": {"width": 100, "height": 100},
                        "mimetype": "image/png",
                    },
                },
                {
                    "type": "UPDATE_CHART",
                    "figureId": "chartId",
                    "definition": {
                        "type": "line",
                        "title": "Chart Title",
                        "dataSets": ["A1:B2", "C1:D2"],
                    },
                },
                {
                    "type": "UPDATE_FIGURE",
                    "figureId": "chartId",
                    "offset": {"x": 5, "y": 10},
                },
                {
                    "type": "SELECT_FIGURE",
                    "figureId": "chartId",
                },
                {
                    "type": "DELETE_FIGURE",
                    "figureId": "chartId",
                },
                {"type": "SET_BORDER", "border": None, "col": 10, "row": 10, "sheetId": "uuid"},
            ],
        )
