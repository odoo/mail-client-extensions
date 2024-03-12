# -*- coding: utf-8 -*-
from lxml import html

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version

utf8_parser = html.HTMLParser(encoding="utf-8")


@change_version("saas~16.3")
class TestMapShapes(UpgradeCase):
    def prepare(self):
        arch = """
<t name="Map Shapes Test" t-name="website.map_shapes_test">
  <t t-call="website.layout">
    <t t-set="pageName" t-value="'map shapes test'"/>
    <div id="wrap" class="oe_structure oe_empty">
      <section class="s_text_block pt40 pb40">
          <div class="container s_allow_columns">
              <img class="img img-fluid mx-auto"
                  src="/web_editor/image_shape/website.s_text_image_default_image/web_editor/basic/bsc_square_2.svg"
                  data-shape="web_editor/basic/bsc_square_2"
                  data-original-mimetype="image/jpeg"
                  data-file-name="s_text_image.svg"
                  data-shape-color=";;;;"
              />
              <img class="img img-fluid mx-auto"
                  src="/web_editor/image_shape/website.s_company_team_image_3/web_editor/basic/bsc_square_3.svg"
                  data-shape="web_editor/basic/bsc_square_3"
                  data-original-mimetype="image/jpeg"
                  data-file-name="s_text_image.svg"
                  data-shape-color=";;;;"
              />
              <img class="img img-fluid mx-auto"
                  src="/web_editor/image_shape/website.whatever/web_editor/pattern/pattern_labyrinth.svg"
                  data-shape="web_editor/pattern/pattern_labyrinth"
                  data-original-mimetype="image/jpeg"
                  data-file-name="s_text_image.svg"
                  data-shape-color=";;;;"
              />
          </div>
      </section>
    </div>
  </t>
</t>
        """
        view = self.env["ir.ui.view"].create(
            {
                "name": "Map Shapes Test",
                "type": "qweb",
                "key": "website.map_shapes_test",
                "website_id": self.env.ref("website.default_website").id,
                "arch": arch.replace("\\\n", ""),
            }
        )
        return {"view_id": view.id}

    def check(self, init):
        arch = self.env["ir.ui.view"].browse(init["view_id"]).arch_db
        root_el = html.fromstring(f"<wrap>{arch}</wrap>", parser=utf8_parser)
        image_els = root_el.xpath("//img")
        # Image 0
        self.assertEqual(
            image_els[0].get("src"),
            "/web_editor/image_shape/website.s_text_image_default_image/web_editor/geometric/geo_square_2.svg",
            "Image source should have been mapped",
        )
        self.assertEqual(
            image_els[0].get("data-shape"),
            "web_editor/geometric/geo_square_2",
            "Image shape should have been mapped",
        )
        # Image 1
        self.assertEqual(
            image_els[1].get("src"),
            "/web_editor/image_shape/website.s_company_team_image_3/web_editor/geometric/geo_square_3.svg",
            "Image source should have been mapped",
        )
        self.assertEqual(
            image_els[1].get("data-shape"),
            "web_editor/geometric/geo_square_3",
            "Image shape should have been mapped",
        )
        # Image 2
        self.assertEqual(
            image_els[2].get("src"),
            "/web_editor/image_shape/website.whatever/web_editor/pattern/pattern_labyrinth.svg",
            "Image source should have been unchanged",
        )
        self.assertEqual(
            image_els[2].get("data-shape"),
            "web_editor/pattern/pattern_labyrinth",
            "Image shape should have been unchanged",
        )
