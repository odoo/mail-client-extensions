from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.3")
class TestMailLinkPreviewMessage(UpgradeCase):
    url_1 = "https://link-preview.com/test"
    url_2 = "https://link-preview-other.com/test"

    def prepare(self):
        message_1 = self.env["mail.message"].create({"body": "body message 1"})
        message_2 = self.env["mail.message"].create({"body": "body message 2"})
        self.env["mail.link.preview"].create(
            [
                {"source_url": self.url_1, "message_id": message_1.id, "is_hidden": False},
                {"source_url": self.url_1, "message_id": message_2.id, "is_hidden": False},
                {"source_url": self.url_2, "message_id": message_1.id, "is_hidden": True},
                {"source_url": self.url_2, "message_id": message_2.id, "is_hidden": False},
            ]
        )
        return {"message_1": message_1.id, "message_2": message_2.id}

    def check(self, init):
        link_previews = self.env["mail.link.preview"].search([])
        self.assertEqual(len(link_previews), 2)
        message_link_previews = self.env["mail.message.link.preview"].search([])
        self.assertEqual(len(message_link_previews), 4)

        message_1 = self.env["mail.message"].browse(init["message_1"])
        message_2 = self.env["mail.message"].browse(init["message_2"])
        self.assertEqual(len(message_1.message_link_preview_ids), 2)
        self.assertFalse(
            message_1.message_link_preview_ids.filtered(
                lambda message_link_preview: message_link_preview.link_preview_id.source_url == self.url_1
            ).is_hidden
        )
        self.assertTrue(
            message_1.message_link_preview_ids.filtered(
                lambda message_link_preview: message_link_preview.link_preview_id.source_url == self.url_2
            ).is_hidden
        )
        self.assertEqual(len(message_2.message_link_preview_ids), 2)
        self.assertFalse(
            message_2.message_link_preview_ids.filtered(
                lambda message_link_preview: message_link_preview.link_preview_id.source_url == self.url_1
            ).is_hidden
        )
        self.assertFalse(
            message_2.message_link_preview_ids.filtered(
                lambda message_link_preview: message_link_preview.link_preview_id.source_url == self.url_2
            ).is_hidden
        )
