# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version

try:
    from odoo.modules.module import read_manifest
except ImportError:
    read_manifest = None


@change_version("saas~14.3")
class BaseAssetCase(UpgradeCase, abstract=True):
    test_sequence = 42

    def assertAsset(self, view_id, values):
        if not isinstance(values, list):
            values = [values]

        # TODO: remove this horror
        if util.column_exists(self.env.cr, "ir_asset", "path"):

            def rename_glob_into_path(val):
                val["path"] = val.pop("glob", None)
                return val

            values = [rename_glob_into_path(x) for x in values]

        self.assertFalse(self.env["ir.ui.view"].browse(view_id).exists())

        ir_asset = self.env["ir.asset"].search([("name", "ilike", f"view_id:{view_id}")])
        self.assertRecordValues(ir_asset, values)

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
                        <xpath expr="//script[last()]" position="after">
                            <script type="text/javascript" src="/web/static/somefile2.js" />
                        </xpath>
                    </data>
                """,
                "inherit_id": assets_common,
            },
        )

        other_asset = self.make_view(
            {
                "arch": """
                    <data>
                        <xpath expr="//script[@src='/web/static/somefile2.js']" position="replace">
                        </xpath>
                    </data>
                """,
                "inherit_id": assets_common,
            },
        )
        return {"asset_id": asset.id, "other_asset_id": other_asset.id}

    def check(self, init):
        self.assertAsset(
            init["asset_id"],
            [
                {
                    "bundle": "web.assets_common",
                    "directive": "append",
                    "glob": "/web/static/somefile.js",
                    "target": False,
                    "active": True,
                },
                {
                    "bundle": "web.assets_common",
                    "directive": "append",
                    "glob": "/web/static/somefile2.js",
                    "target": False,
                    "active": True,
                },
            ],
        )

        self.assertAsset(
            init["other_asset_id"],
            {
                "bundle": "web.assets_common",
                "directive": "remove",
                "glob": "/web/static/somefile2.js",
                "target": False,
                "active": True,
            },
        )


class TestAssetWithComment(BaseAssetCase):
    def prepare(self):
        assets_common = util.ref(self.env.cr, "web.assets_common")
        self.assertIsNotNone(assets_common)
        comment_child_view = self.make_view(
            {
                "arch": """
                    <data>
                        <!-- <xpath expr="//script[last()]" position="after"> -->
                        <!--   <script type="text/javascript" src="/web/static/somefile2.js" /> -->
                        <!-- </xpath> -->
                        <xpath expr="//script[last()]" position="after">
                            <script type="text/javascript" src="/web/static/somefile3.js" />
                        </xpath>
                    </data>
                """,
                "inherit_id": assets_common,
            }
        )
        return {"comment_child_view": comment_child_view.id}

    def check(self, init):
        self.assertAsset(
            init["comment_child_view"],
            {
                "bundle": "web.assets_common",
                "directive": "append",
                "glob": "/web/static/somefile3.js",
                "target": False,
                "active": True,
            },
        )


class TestAssetExtendsFromAttributes(BaseAssetCase):
    def prepare(self):
        bundle_view = self.make_view(
            {
                "arch": """
                    <t name="asset">
                        <script type="text/javascript" src="/web/static/somefile.js" />
                        <link type="text/css" href="/web/static/somestyle.css" rel="stylesheet" />
                    </t>
                """
            },
        )
        calling_view = self.make_calling_view(bundle_view.key)

        child_view_1 = self.make_view(
            {
                "arch": """
                    <data>
                        <xpath expr="//script[@src='/web/static/somefile.js']" position="attributes">
                            <attribute name="src">/web/static/somenewfile.js</attribute>
                        </xpath>
                    </data>
                """,
                "inherit_id": bundle_view.id,
            },
        )

        child_view_2 = self.make_view(
            {
                "arch": """
                    <data>
                        <xpath expr="//link[@href='/web/static/somestyle.css']" position="attributes">
                            <attribute name="href">/web/static/somenewstyle.css</attribute>
                        </xpath>
                    </data>
                """,
                "inherit_id": bundle_view.id,
            },
        )

        return {
            "calling_view_id": calling_view.id,
            "bundle_view_key": bundle_view.key,
            "bundle_view_id": bundle_view.id,
            "child_view_1_id": child_view_1.id,
            "child_view_2_id": child_view_2.id,
        }

    def check(self, check):
        self.assertTrue(self.env["ir.ui.view"].browse(check["calling_view_id"]).exists())
        self.assertAsset(
            check["bundle_view_id"],
            [
                {
                    "bundle": check["bundle_view_key"],
                    "directive": "append",
                    "glob": "/web/static/somefile.js",
                    "target": False,
                    "sequence": 16,
                    "active": True,
                },
                {
                    "bundle": check["bundle_view_key"],
                    "directive": "append",
                    "glob": "/web/static/somestyle.css",
                    "target": False,
                    "sequence": 16,
                    "active": True,
                },
            ],
        )
        self.assertAsset(
            check["child_view_1_id"],
            {
                "bundle": check["bundle_view_key"],
                "directive": "replace",
                "glob": "/web/static/somenewfile.js",
                "target": "/web/static/somefile.js",
                "sequence": 32,
                "active": True,
            },
        )
        self.assertAsset(
            check["child_view_2_id"],
            {
                "bundle": check["bundle_view_key"],
                "directive": "replace",
                "glob": "/web/static/somenewstyle.css",
                "target": "/web/static/somestyle.css",
                "sequence": 32,
                "active": True,
            },
        )


class TestAssetResequence(BaseAssetCase):
    def prepare(self):
        """
        Here is a convoluted use case.

          A
          |
          B
         ___
        / | \
        C D E

        # | Var Name     | Prio | Description
        A | bundle_view  | 16   | append -> somefile.js
        B | child_view_1 | 200  | after somefile.js -> custom.js
        C | child_view_2 | 16   | replace custom.js -> custom.replaced.js
        D | child_view_3 | 100  | before custom.replaced.js -> another.js
        E | child_view_4 | 110  | remove custom.replaced.js
        """

        bundle_view = self.make_view(
            {
                "arch": """
                    <t name="asset">
                        <script type="text/javascript" src="/web/static/somefile.js" />
                    </t>
                """
            },
        )
        calling_view = self.make_calling_view(bundle_view.key)

        child_view_1 = self.make_view(
            {
                "arch": """
                    <data>
                        <xpath expr="//script[last()]" position="after">
                            <script type="text/javascript" src="web/static/custom.js" />
                        </xpath>
                    </data>
                """,
                "inherit_id": bundle_view.id,
                "priority": 200,
            },
        )

        child_view_2 = self.make_view(
            {
                "arch": """
                    <data>
                        <xpath expr="//script[@src='web/static/custom.js']" position="attributes">
                            <attribute name="src">/web/static/custom.replaced.js</attribute>
                        </xpath>
                    </data>
                """,
                "inherit_id": child_view_1.id,
            },
        )

        child_view_3 = self.make_view(
            {
                "arch": """
                    <data>
                        <xpath expr="//script[@src='/web/static/custom.replaced.js']" position="before">
                            <script type="text/javascript" src="web/static/another.js" />
                        </xpath>
                    </data>
                """,
                "priority": 100,
                "inherit_id": child_view_1.id,
            },
        )

        child_view_4 = self.make_view(
            {
                "arch": """
                    <data>
                        <xpath expr="//script[@src='/web/static/custom.replaced.js']" position="replace">
                        </xpath>
                    </data>
                """,
                "priority": 110,
                "inherit_id": child_view_1.id,
            },
        )

        self.assertEqual(bundle_view.priority, 16)
        self.assertEqual(child_view_1.priority, 200)
        self.assertEqual(child_view_2.priority, 16)
        self.assertEqual(child_view_3.priority, 100)
        self.assertEqual(child_view_4.priority, 110)

        return {
            "calling_view_id": calling_view.id,
            "bundle_view_key": bundle_view.key,
            "bundle_view_id": bundle_view.id,
            "child_view_1_id": child_view_1.id,
            "child_view_2_id": child_view_2.id,
            "child_view_3_id": child_view_3.id,
            "child_view_4_id": child_view_4.id,
        }

    def check(self, check):
        self.assertTrue(self.env["ir.ui.view"].browse(check["calling_view_id"]).exists())
        self.assertAsset(
            check["bundle_view_id"],
            {
                "bundle": check["bundle_view_key"],
                "directive": "append",
                "target": False,
                "glob": "/web/static/somefile.js",
                "sequence": 16,
                "active": True,
            },
        )
        self.assertAsset(
            check["child_view_1_id"],
            {
                "bundle": check["bundle_view_key"],
                "directive": "append",
                "target": False,
                "glob": "web/static/custom.js",
                "sequence": 200,  # -> child1 priority
                "active": True,
            },
        )
        self.assertAsset(
            check["child_view_2_id"],
            {
                "bundle": check["bundle_view_key"],
                "directive": "replace",
                "target": "web/static/custom.js",
                "glob": "/web/static/custom.replaced.js",
                "sequence": 216,  # -> child1 + child2 priority
                "active": True,
            },
        )
        self.assertAsset(
            check["child_view_3_id"],
            {
                "bundle": check["bundle_view_key"],
                "directive": "before",
                "target": "/web/static/custom.replaced.js",
                "glob": "web/static/another.js",
                "sequence": 316,  # -> child1 + child2 + child3 priority
                "active": True,
            },
        )
        self.assertAsset(
            check["child_view_4_id"],
            {
                "bundle": check["bundle_view_key"],
                "directive": "remove",
                "target": False,
                "glob": "/web/static/custom.replaced.js",
                "sequence": 326,  # -> child1 + child2 + child4 priority
                "active": True,
            },
        )
