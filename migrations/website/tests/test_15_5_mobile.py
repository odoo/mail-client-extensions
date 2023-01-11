# -*- coding: utf-8 -*-

import re

from lxml import html

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version

utf8_parser = html.HTMLParser(encoding="utf-8")


@change_version("16.0")
class TestHiddenOnMobile(UpgradeCase):
    def prepare(self):
        arch = """
<t name="Used Assets Test" t-name="website.hidden_on_mobile_test">
  <t t-call="website.layout">
    <t t-set="pageName" t-value="'hidden on mobile test'"/>
    <div id="wrap" class="oe_structure oe_empty">
      <section class="s_text_block pt40 pb40">
          <div class="container s_allow_columns">
              <p>Visible on mobile</p>
          </div>
      </section>
      <section class="s_text_block pt40 pb40 d-none d-md-block">
          <div class="container s_allow_columns">
              <p>Hidden on mobile</p>
          </div>
      </section>
      <section class="s_text_block pt40 pb40 d-none d-lg-block">
          <div class="container s_allow_columns">
              <p>Hidden on mobile (with lg threshold).</p>
          </div>
      </section>
    </div>
  </t>
</t>
        """
        view = self.env["ir.ui.view"].create(
            {
                "name": "Hidden on Mobile Test",
                "type": "qweb",
                "key": "website.used_assets_test",
                "website_id": self.env.ref("website.default_website").id,
                "arch": arch.replace("\\\n", ""),
            }
        )
        return {"view_id": view.id}

    def check(self, init):
        arch = self.env["ir.ui.view"].browse(init["view_id"]).arch_db
        root_el = html.fromstring(f"<wrap>{arch}</wrap>", parser=utf8_parser)
        sections = root_el.xpath("//section")
        # Visible on mobile
        classes = re.split(r"\s+", sections[0].get("class"))
        self.assertNotIn("o_snippet_mobile_invisible", classes, "Should not be invisible on mobile")
        self.assertNotIn("data-invisible", sections[0], "Should not be considered invisible")

        # Invisible on mobile
        classes = re.split(r"\s+", sections[1].get("class"))
        self.assertIn("o_snippet_mobile_invisible", classes, "Should be invisible on mobile")
        self.assertEqual(sections[1].get("data-invisible"), "1", "Should be considered invisible")

        classes = re.split(r"\s+", sections[2].get("class"))
        self.assertIn("o_snippet_mobile_invisible", classes, "Should be invisible on mobile")
        self.assertEqual(sections[2].get("data-invisible"), "1", "Should be considered invisible")
