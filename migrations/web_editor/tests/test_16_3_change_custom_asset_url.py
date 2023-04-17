# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations.testing import (
    UpgradeCase,
    change_version,
)


@change_version("saas~16.3")
class TestRenamCustomAssets(UpgradeCase):
    def prepare(self):
        url = "/web_editor/static/src/scss/bootstrap_overridden_backend.scss"
        content = """
            $prevent-backend-colors-alteration: true;
        """
        self.env["web_editor.assets"].save_asset(
            url,
            "web.assets_frontend",
            content,
            "scss",
        )
        asset = self.env["ir.asset"].search([], order="id desc", limit=1)
        attachment = self.env["ir.attachment"].search([], order="id desc", limit=1)
        custom_url = "/web_editor/static/src/scss/bootstrap_overridden_backend.custom.web.assets_frontend.scss"
        self.assertEqual(asset.path, custom_url)
        self.assertEqual(attachment.url, custom_url)
        return {
            "asset_id": asset.id,
            "attachment_id": attachment.id,
        }

    def check(self, init):
        asset_id = init["asset_id"]
        asset = self.env["ir.asset"].browse(asset_id)
        custom_url = "/_custom/web.assets_frontend/web_editor/static/src/scss/bootstrap_overridden_backend.scss"
        self.assertEqual(asset.path, custom_url)
        attachment_id = init["attachment_id"]
        attachment = self.env["ir.attachment"].browse(attachment_id)
        self.assertEqual(attachment.url, custom_url)
