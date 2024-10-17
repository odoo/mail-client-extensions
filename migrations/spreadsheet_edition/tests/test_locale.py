from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.addons.base.maintenance.migrations.util import json


@change_version("saas~17.5")
class TestSpreadsheetUpdateLocale(UpgradeCase):
    def prepare(self):
        commands = {
            "type": "REMOTE_REVISION",
            "commands": [
                {
                    "type": "UPDATE_LOCALE",
                    "locale": {
                        "code": "en_US",
                    },
                },
                {
                    "type": "UPDATE_LOCALE",
                    "locale": {
                        "code": "fr_FR",
                    },
                },
                {
                    "type": "UPDATE_LOCALE",
                    "locale": {
                        "code": "unknown_locale",
                    },
                },
            ],
        }
        field_name = "revision_uuid" if util.version_gte("saas~17.2") else "revision_id"
        revision_id = self.env["spreadsheet.revision"].create(
            [
                {
                    "res_id": 1200,
                    "res_model": "spreadsheet",
                    "commands": json.dumps(commands),
                    field_name: "B",
                    "parent_revision_id": False if util.version_gte("saas~17.2") else "START_REVISION",
                },
            ]
        )
        return revision_id.id

    def check(self, revision_id):
        revisions = self.env["spreadsheet.revision"].browse(revision_id)

        data = json.loads(revisions[0].commands)
        self.assertEqual(data["commands"][0]["locale"]["weekStart"], 7)
        self.assertEqual(data["commands"][1]["locale"]["weekStart"], 1)
        self.assertEqual(data["commands"][2]["locale"]["weekStart"], 1)
