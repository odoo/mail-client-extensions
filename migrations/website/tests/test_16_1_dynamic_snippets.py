# -*- coding: utf-8 -*-

import re

from lxml import html

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version

utf8_parser = html.HTMLParser(encoding="utf-8")


@change_version("saas~16.1")
class TestDynamicEmpty(UpgradeCase):
    def prepare(self):
        arch = """
<t name="Dynamic Empty Test" t-name="website.dynamic_empty_test">
  <t t-call="website.layout">
    <t t-set="pageName" t-value="'dynamic empty test'"/>
    <div id="wrap" class="oe_structure oe_empty">
        <section data-snippet="s_dynamic_snippet" data-name="Dynamic Snippet"
                class="s_dynamic_snippet s_dynamic pt32 pb32 d-none">
            Non-hidden before fix.
        </section>
        <section data-snippet="s_dynamic_snippet" data-name="Dynamic Snippet"
                class="s_dynamic_snippet s_dynamic pt32 pb32 o_dynamic_empty">
            Non-hidden after fix.
        </section>
        <section data-snippet="s_dynamic_snippet" data-name="Dynamic Snippet"
                class="s_dynamic_snippet s_dynamic pt32 pb32 d-none d-md-block">
            Broken "Hidden" before fix.
        </section>
        <section data-snippet="s_dynamic_snippet" data-name="Dynamic Snippet"
                class="s_dynamic_snippet s_dynamic pt32 pb32 o_dynamic_empty d-none d-md-block">
            Hidden after fix.
        </section>
        <section data-snippet="s_dynamic_snippet" data-name="Dynamic Snippet"
                class="s_dynamic_snippet s_dynamic pt32 pb32 d-none d-lg-block">
            Broken "Hidden" before fix (with lg threshold).
        </section>
        <section data-snippet="s_dynamic_snippet" data-name="Dynamic Snippet"
                class="s_dynamic_snippet s_dynamic pt32 pb32 o_dynamic_empty d-none d-lg-block">
            Hidden after fix (with lg threshold).
        </section>
    </div>
  </t>
</t>
        """
        view = self.env["ir.ui.view"].create(
            {
                "name": "Dynamic Empty Test",
                "type": "qweb",
                "key": "website.used_assets_test",
                "website_id": self.env.ref("website.default_website").id,
                "arch": arch.replace(r"\n", ""),
            }
        )
        return {"view_id": view.id}

    def check(self, init):
        arch = self.env["ir.ui.view"].browse(init["view_id"]).arch_db
        root_el = html.fromstring(f"<wrap>{arch}</wrap>", parser=utf8_parser)
        sections = root_el.xpath("//section")
        # Non-hidden and from before fix.
        classes = re.split(r"\s+", sections[0].get("class"))
        self.assertNotIn("d-none", classes, "Should not be d-none")
        self.assertIn("o_dynamic_empty", classes, "Should be dynamic empty")
        # Non-hidden and from after fix.
        classes = re.split(r"\s+", sections[1].get("class"))
        self.assertNotIn("d-none", classes, "Should not be d-none")
        self.assertIn("o_dynamic_empty", classes, "Should be dynamic empty")
        # Hidden and from before fix.
        classes = re.split(r"\s+", sections[2].get("class"))
        self.assertIn("o_dynamic_empty", classes, "Should be dynamic empty")
        self.assertIn("d-none", classes, "Should be hidden on mobile with d-none")
        self.assertIn("d-md-block", classes, "Should be visible on desktop with d-md-block")
        # Hidden and from after fix.
        classes = re.split(r"\s+", sections[3].get("class"))
        self.assertIn("o_dynamic_empty", classes, "Should be dynamic empty")
        self.assertIn("d-none", classes, "Should be hidden on mobile with d-none")
        self.assertIn("d-md-block", classes, "Should be visible on desktop with d-md-block")
        # Hidden and from before fix (with lg threshold).
        classes = re.split(r"\s+", sections[4].get("class"))
        self.assertIn("o_dynamic_empty", classes, "Should be dynamic empty")
        self.assertIn("d-none", classes, "Should be hidden on mobile with d-none")
        self.assertIn("d-lg-block", classes, "Should be visible on desktop with d-lg-block")
        # Hidden and from after fix (with lg threshold).
        classes = re.split(r"\s+", sections[5].get("class"))
        self.assertIn("o_dynamic_empty", classes, "Should be dynamic empty")
        self.assertIn("d-none", classes, "Should be hidden on mobile with d-none")
        self.assertIn("d-lg-block", classes, "Should be visible on desktop with d-lg-block")
