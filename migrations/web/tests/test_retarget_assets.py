from odoo.addons.base.maintenance.migrations.base.tests.test_assets_management import BaseAssetCase
from odoo.addons.base.maintenance.migrations.testing import change_version


@change_version("saas~14.5")
class TestRetargetAsset(BaseAssetCase):
    def prepare(self):
        orig_path_1 = "/website/static/src/js/user_custom_javascript.js"
        orig_path_2 = "/web/static/src/scss/navbar_mobile.scss"
        bundle_view = self.make_view(
            {
                "arch": f"""
                    <t name="asset">
                        <script type="text/javascript" src="{orig_path_1}" />
                        <link type="text/css" href="{orig_path_2}" rel="stylesheet" />
                    </t>
                """
            },
        )
        calling_view = self.make_calling_view(bundle_view.key)

        new_path_1 = f"/website/static/src/js/user_custom_javascript.custom.{bundle_view.key}.js"
        child_view_1 = self.make_view(
            {
                "arch": f"""
                    <data>
                        <xpath expr="//script[@src='{orig_path_1}']" position="attributes">
                            <attribute name="src">{new_path_1}</attribute>
                        </xpath>
                    </data>
                """,
                "inherit_id": bundle_view.id,
                "name": new_path_1,
            },
        )

        new_path_2 = f"/web/static/src/scss/navbar_mobile.custom.{bundle_view.key}.scss"
        child_view_2 = self.make_view(
            {
                "arch": f"""
                    <data>
                        <xpath expr="//link[@href='{orig_path_2}']" position="attributes">
                            <attribute name="href">{new_path_2}</attribute>
                        </xpath>
                    </data>
                """,
                "inherit_id": bundle_view.id,
                "name": new_path_2,
            },
        )

        return {
            "calling_view_id": calling_view.id,
            "bundle_view_key": bundle_view.key,
            "child_view_1_id": child_view_1.id,
            "child_view_2_id": child_view_2.id,
            "new_path_1": new_path_1,
            "new_path_2": new_path_2,
            "orig_path_1": orig_path_1,
            "orig_path_2": orig_path_2,
        }

    def check(self, check):
        self.assertTrue(self.env["ir.ui.view"].browse(check["calling_view_id"]).exists())

        # views 1 and 2 must have been migrated
        child_view_1_id = check["child_view_1_id"]
        child_view_2_id = check["child_view_2_id"]
        self.assertFalse(self.env["ir.ui.view"].browse(child_view_1_id).exists())
        self.assertFalse(self.env["ir.ui.view"].browse(child_view_2_id).exists())
        self.assertTrue(self.env["ir.asset"].search([("name", "ilike", f"view_id:{child_view_1_id}")]))
        self.assertTrue(self.env["ir.asset"].search([("name", "ilike", f"view_id:{child_view_2_id}")]))

        # the first child view corresponding asset must still have the same target
        self.assertAsset(
            child_view_1_id,
            {
                "bundle": check["bundle_view_key"],
                "directive": "replace",
                "glob": check["new_path_1"],
                "target": check["orig_path_1"],
                "active": True,
            },
        )

        # the second child view corresponding asset must have its target replaced
        self.assertAsset(
            child_view_2_id,
            {
                "bundle": check["bundle_view_key"],
                "directive": "replace",
                "glob": check["new_path_2"],
                "target": "web/static/src/legacy/scss/navbar_mobile.scss",  # notice the '/legacy' part
                "active": True,
            },
        )
