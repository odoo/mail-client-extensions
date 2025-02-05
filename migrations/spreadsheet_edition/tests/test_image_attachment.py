from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.addons.base.maintenance.migrations.util import json


@change_version("17.0")
class TestSpreadsheetImageAttachment(UpgradeCase):
    def prepare(self):
        if not util.table_exists(self.env.cr, "spreadsheet_revision"):
            return None
        spreadsheet_id = 2
        attachment_res_id = 99  # another spreadsheet record
        image_1 = self.env["ir.attachment"].create(
            {"name": "Attachment", "res_model": "spreadsheet", "res_id": attachment_res_id}
        )
        image_2 = self.env["ir.attachment"].create(
            {
                "name": "Attachment",
                "res_model": "spreadsheet",
                "res_id": attachment_res_id,
                "access_token": "123",
            }
        )
        base_cmd = {
            "type": "CREATE_IMAGE",
            "figureId": "1",
            "position": {"x": 1, "y": 2},
            "size": {"width": 100, "height": 100},
            "definition": None,
        }
        simple = {
            "path": f"/web/image/{image_1.id}",
            "size": {"width": 100, "height": 100},
            "mimetype": "image/png",
        }
        with_access_token = {
            "path": f"/web/image/{image_2.id}?access_token={image_2.access_token}",
            "size": {"width": 100, "height": 100},
            "mimetype": "image/png",
        }
        b64 = {
            "path": "data:image/png;base64,iVBORw0KGgoAA",
            "size": {"width": 100, "height": 100},
            "mimetype": "image/png",
        }
        commands = {
            "type": "REMOTE_REVISION",
            "commands": [
                dict(base_cmd, definition=simple),
                dict(base_cmd, definition=with_access_token),
                dict(base_cmd, definition=b64),
            ],
        }
        revision = self.env["spreadsheet.revision"].create(
            {
                "res_id": spreadsheet_id,
                "res_model": "spreadsheet",
                "commands": json.dumps(commands),
                "parent_revision_id": "A",
                "revision_id": "B",
            }
        )
        return {
            "revision_id": revision.id,
            "original_attachment_id_1": image_1.id,
            "original_attachment_id_2": image_2.id,
        }

    def check(self, init):
        revision_id = init["revision_id"]
        revision = self.env["spreadsheet.revision"].browse(revision_id)
        commands = json.loads(revision.commands)["commands"]
        attachment_id_1 = int(commands[0]["definition"]["path"].split("/")[3].split("?")[0])
        attachment_id_2 = int(commands[1]["definition"]["path"].split("/")[3].split("?")[0])
        attachment_2 = self.env["ir.attachment"].browse(attachment_id_2)
        self.assertNotEqual(attachment_id_1, init["original_attachment_id_1"])
        self.assertNotEqual(attachment_id_2, init["original_attachment_id_2"])
        self.assertEqual(
            [cmd["definition"] for cmd in commands],
            [
                {
                    "path": f"/web/image/{attachment_id_1}",
                    "size": {"width": 100, "height": 100},
                    "mimetype": "image/png",
                },
                {
                    "path": f"/web/image/{attachment_id_2}?access_token={attachment_2.access_token}",
                    "size": {"width": 100, "height": 100},
                    "mimetype": "image/png",
                },
                {
                    "path": "data:image/png;base64,iVBORw0KGgoAA",
                    "size": {"width": 100, "height": 100},
                    "mimetype": "image/png",
                },
            ],
        )
