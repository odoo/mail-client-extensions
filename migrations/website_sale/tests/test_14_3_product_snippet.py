# -*- coding: utf-8 -*-

from lxml import html

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version

utf8_parser = html.HTMLParser(encoding="utf-8")


@change_version("14.3")
class TestProductSnippet(UpgradeCase):
    def prepare(self):
        arch = """
<t name="Product Snippet Test" t-name="website_sale.product_snippet_test">
  <t t-call="website.layout">
    <t t-set="pageName" t-value="'product snippet test'"/>
    <div id="wrap" class="oe_structure oe_empty">
      <section class="s_wsale_products_recently_viewed o_snippet_invisible pt24 pb24 o_colored_level\\
        d-none"
        style="min-height: 400px;" data-snippet="s_products_recently_viewed"
        data-name="Viewed Products" data-invisible="1">
        <div class="container">
          <h3 class="text-center mb32 o_default_snippet_text">Recently Viewed Products</h3>
          <div class="slider o_not_editable"/>
        </div>
      </section>
      <section class="s_wsale_products_recently_viewed o_snippet_invisible pt24 pb24 o_colored_level\\
        o_cc o_cc3 o_half_screen_height oe_img_bg o_bg_img_center d-none"
        style="min-height: 400px; position: relative; background-image: url(\\
          '/website_sale/static/src/img/apps.png');"
        data-snippet="s_products_recently_viewed" data-name="Viewed Products" data-invisible="1"
        data-oe-shape-data="{'shape':'web_editor/Origins/01','colors':{'c2':'#7c6576','c5':'#508DD2'},\\
          flip':['x','y']}"
        data-original-id="1519" data-original-src="/website_sale/static/src/img/apps.png"
        data-mimetype="image/jpeg" data-resize-width="1920">
        <div class="o_we_shape o_web_editor_Origins_01"
          style="background-image: url(\\
            '/web_editor/shape/web_editor/Origins/01.svg?c2=%237c6576&amp;c5=%23508DD2&amp;flip=xy');\\
          background-position: 50% 0%;"/>
        <div class="container">
          <h3 class="text-center mb32 o_default_snippet_text">Recently Viewed Products</h3>
          <div class="slider o_not_editable"/>
        </div>
        <a class="o_scroll_button rounded-circle align-items-center justify-content-center mx-auto\\
          mb-1" href="#" title="Scroll down to next section"
          style="background-color: rgb(79, 226, 221) !important; color: rgb(171, 246, 244) !important;">
          <i class="fa fa-angle-down fa-3x"/>
        </a>
      </section>
    </div>
  </t>
</t>
        """
        view_ids = self.env["ir.ui.view"].create(
            {
                "name": "Product Snippet Test",
                "type": "qweb",
                "key": "website_sale.product_snippet_test",
                "website_id": self.env.ref("website.default_website").id,
                "arch": arch.replace("\\\n", ""),
            }
        )
        return {"view_id": view_ids.id}

    def check(self, init):
        view_id = self.env["ir.ui.view"].browse(init["view_id"])
        body = html.fromstring(view_id.arch, parser=utf8_parser)
        snippet_els = body.xpath("//section[@data-snippet='s_dynamic_snippet_products']")
        self.assertEqual(2, len(snippet_els))

        for el in snippet_els:
            dynamic_snippet_template = el.xpath(".//div[hasclass('dynamic_snippet_template')]")
            self.assertEqual(1, len(dynamic_snippet_template))

            filter_id = self.env["website.snippet.filter"].browse(int(el.get("data-filter-id")))
            self.assertEqual("Recently Viewed Products", filter_id.name)
            template_key = el.get("data-template-key")
            self.assertEqual("website_sale.dynamic_filter_template_product_product_add_to_cart", template_key)
            category_id = el.get("data-product-category-id")
            self.assertEqual("all", category_id)
