# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations.base.tests.test_assets_management import BaseAssetCase


class TestAssetWithWebsite(BaseAssetCase):
    def prepare(self):
        """
        This test will verify if the website columns are effectively passed
        from the assets definition QWeb views to the new ir_asset model.
        """
        website = self.env["website"].create({"name": "test_website"})

        # view linked to a website
        view = self.make_view(
            {
                "arch": """
                    <t name="asset">
                        <script type="text/javascript" src="/web/static/somefile.js" />
                    </t>
                """,
                "website_id": website.id,
            },
            {"module": "somemodule", "name": "view"},
        )
        calling_view = self.make_calling_view(view.key)

        # view linked to a website AND coming from a theme
        theme_template = self.env["theme.ir.ui.view"].create({"name": "test_theme_template"})
        view_from_theme = self.make_view(
            {
                "arch": """
                    <t name="asset">
                        <script type="text/javascript" src="/web/static/somefile.js" />
                    </t>
                """,
                "theme_template_id": theme_template.id,
                "website_id": website.id,
            },
            {"module": "somemodule", "name": "view_from_theme"},
        )
        calling_view_from_theme = self.make_calling_view(view_from_theme.key)

        self.assertEqual(view.key, "somemodule.view")
        self.assertEqual(view_from_theme.key, "somemodule.view_from_theme")

        return {
            "view_id": view.id,
            "view_key": view.key,
            "view_from_theme_id": view_from_theme.id,
            "view_from_theme_key": view_from_theme.key,
            "calling_view_id": calling_view.id,
            "calling_view_from_theme_id": calling_view_from_theme.id,
            "website_id": website.id,
        }

    def check(self, check):
        self.assertTrue(self.env["ir.ui.view"].browse(check["calling_view_id"]).exists())
        self.assertTrue(self.env["ir.ui.view"].browse(check["calling_view_from_theme_id"]).exists())

        # The first view should have been migrated into an ir_asset linked to the proper website.
        self.assertAsset(
            check["view_id"],
            {
                "bundle": check["view_key"],
                "directive": "append",
                "glob": "/web/static/somefile.js",
                "target": False,
                "active": True,
                "website_id": check["website_id"],
                "theme_template_id": None,
            },
        )

        # The view from theme should not have created any ir_asset by the migration.
        # The asset should instead be migrated through the corresponding theme upgrade,
        # which is not covered by this test.
        asset_from_theme = self.env["ir.asset"].search([("bundle", "=", check["view_from_theme_key"])])
        self.assertFalse(asset_from_theme.exists())
