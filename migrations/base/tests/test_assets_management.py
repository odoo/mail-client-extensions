# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version

try:
    from odoo.modules.module import read_manifest
except ImportError:
    read_manifest = None


@change_version("14.3")
class BaseAssetCase(UpgradeCase):
    test_sequence = 42

    def prepare(self):
        pass

    def check(self, init):
        pass

    def assertAsset(self, view_id, values):
        self.assertFalse(self.env["ir.ui.view"].browse(view_id).exists())

        ir_asset = self.env["ir.asset"].search([("name", "ilike", f"view_id:{view_id}")])
        self.assertRecordValues(ir_asset, [values])

    def make_view(self, view_values, irmodeldata_values=None):
        values = {
            "name": "test_asset",
            "type": "qweb",
        }
        values.update(view_values)

        imd_vals = None
        if irmodeldata_values:
            imd_vals = {"model": "ir.ui.view"}
            imd_vals.update(irmodeldata_values)
            values["key"] = "%s.%s" % (imd_vals["module"], imd_vals["name"])

        view = self.env["ir.ui.view"].create(values)
        if imd_vals:
            imd_vals["res_id"] = view.id
            self.env["ir.model.data"].create(imd_vals)
        return view

    def make_calling_view(self, asset_key, view_values=None, irmodeldata_values=None):
        values = {
            "arch": f"""
                 <div>
                     <t t-call-assets="{asset_key}" />
                 </div>
             """
        }
        if view_values:
            values.update(view_values)
        return self.make_view(values, irmodeldata_values)


class TestSimpleManualAssetIsCalled(BaseAssetCase):
    def prepare(self):
        asset = self.make_view(
            {
                "arch": """
                    <t name="asset">
                        <script type="text/javascript" src="/web/static/somefile.js" />
                    </t>
                """
            },
        )
        calling_view = self.make_calling_view(asset.key)

        return {"asset_id": asset.id, "asset_key": asset.key, "calling_view_id": calling_view.id}

    def check(self, init):
        self.assertTrue(self.env["ir.ui.view"].browse(init["calling_view_id"]).exists())

        self.assertAsset(
            init["asset_id"],
            {
                "bundle": init["asset_key"],
                "directive": "append",
                "glob": "/web/static/somefile.js",
                "target": False,
                "active": True,
            },
        )


class TestSimpleManualAssetIsCalledById(BaseAssetCase):
    def prepare(self):
        asset = self.make_view(
            {
                "arch": """
                    <t name="asset">
                        <script type="text/javascript" src="/web/static/somefile.js" />
                    </t>
                """
            },
        )
        calling_view = self.make_calling_view(asset.id)

        return {"asset_id": asset.id, "asset_key": asset.key, "calling_view_id": calling_view.id}

    def check(self, init):
        self.assertTrue(self.env["ir.ui.view"].browse(init["calling_view_id"]).exists())

        self.assertAsset(
            init["asset_id"],
            {
                "bundle": init["asset_key"],
                "directive": "append",
                "glob": "/web/static/somefile.js",
                "target": False,
                "active": True,
            },
        )


class TestSimpleIrModelDataAssetIsCalled(BaseAssetCase):
    def prepare(self):
        asset = self.make_view(
            {
                "arch": """
                    <t name="asset">
                        <script type="text/javascript" src="/web/static/somefile.js" />
                    </t>
                """
            },
            {"module": "somemodule", "name": "somename"},
        )
        self.assertEqual(asset.key, "somemodule.somename")
        calling_view = self.make_calling_view(asset.key)

        return {"asset_id": asset.id, "asset_key": asset.key, "calling_view_id": calling_view.id}

    def check(self, init):
        self.assertAsset(
            init["asset_id"],
            {
                "bundle": "somemodule.somename",
                "directive": "append",
                "glob": "/web/static/somefile.js",
                "target": False,
                "active": True,
            },
        )

        xml_id = self.env["ir.model.data"].search([("model", "=", "ir.ui.view"), ("res_id", "=", init["asset_id"])])
        self.assertFalse(xml_id.exists())
        self.assertTrue(self.env["ir.ui.view"].browse(init["calling_view_id"]).exists())


class TestAssetExtendsCommon(BaseAssetCase):
    def prepare(self):
        assets_common = util.ref(self.env.cr, "web.assets_common")
        self.assertIsNotNone(assets_common)

        asset = self.make_view(
            {
                "arch": """
                    <data>
                        <xpath expr="//script[last()]" position="after">
                            <script type="text/javascript" src="/web/static/somefile.js" />
                        </xpath>
                    </data>
                """,
                "inherit_id": assets_common,
            },
        )
        return {"asset_id": asset.id, "asset_key": asset.key}

    def check(self, init):
        self.assertAsset(
            init["asset_id"],
            {
                "bundle": "web.assets_common",
                "directive": "append",
                "glob": "/web/static/somefile.js",
                "target": False,
                "active": True,
            },
        )
