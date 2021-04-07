# -*- coding: utf-8 -*-

from lxml import html

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version

utf8_parser = html.HTMLParser(encoding="utf-8")


@change_version("14.5")
class TestProductSearchbarSnippet(UpgradeCase):
    def prepare(self):
        arch = """
<t name="Product Snippet Test" t-name="website_sale.product_searchbar_snippet_test">
  <t t-call="website.layout">
    <t t-set="pageName" t-value="'product searchbar snippet test'"/>
    <div id="wrap" class="oe_structure oe_empty">
      <section class="s_wsale_products_searchbar bg-200 pt48 pb48 o_colored_level" data-vxml="001"\\
        data-snippet="s_products_searchbar" data-name="Products Search">
        <div class="container">
          <div class="row">
            <div class="col-lg-8 offset-lg-2 o_colored_level">
              <h2 class="o_default_snippet_text">Search for a product</h2>
              <p class="o_default_snippet_text">We have amazing products in our shop, check them now !</p>
              <form method="get" data-snippet="s_products_searchbar_input"
                class="o_wsale_products_searchbar_form s_wsale_products_searchbar_input" action="/shop">
                <div role="search" class="input-group">
                  <input type="search" name="search" class="search-query form-control oe_search_box"
                    data-limit="5" data-display-description="true" data-display-price="true"
                    data-display-image="true" placeholder="Search..." autocomplete="off"/>
                  <div class="input-group-append">
                    <button type="submit" class="btn btn-primary oe_search_button"
                      aria-label="Search" title="Search">
                      <i class="fa fa-search">​</i>
                    </button>
                  </div>
                </div>
                <input name="order" type="hidden" class="o_wsale_search_order_by" value=""/>
              </form>
            </div>
          </div>
        </div>
      </section>
      <section class="s_wsale_products_searchbar pt48 pb48 o_colored_level o_half_screen_height"
        data-vxml="001" data-snippet="s_products_searchbar" data-name="Products Search"
        style="background-color: rgb(255, 239, 198) !important; position: relative;"
        data-oe-shape-data="{'shape':'web_editor/Airy/03','colors':{'c5':'#9CC6EF'},'flip':['x','y']}">
        <div class="o_we_shape o_web_editor_Airy_03" style="background-image: url(\\
          '/web_editor/shape/web_editor/Airy/03.svg?c5=%239CC6EF&amp;flip=xy');\\
          background-position: 50% 100%;"/>
        <div class="container-fluid">
          <div class="row">
            <div class="col-lg-8 offset-lg-2 o_colored_level">
              <h2>Search products</h2>
              <p>Keep this text !</p>
              <form method="get" data-snippet="s_products_searchbar_input"
                class="o_wsale_products_searchbar_form s_wsale_products_searchbar_input" action="/shop">
                <div role="search" class="input-group">
                  <input type="search" name="search" class="search-query form-control oe_search_box"
                    data-limit="15" data-display-description="" data-display-price=""
                    data-display-image="" placeholder="Search..." autocomplete="off"/>
                  <div class="input-group-append">
                    <button type="submit" class="btn btn-primary oe_search_button" aria-label="Search"
                      title="Search">
                      <i class="fa fa-search">​</i>
                    </button>
                  </div>
                </div>
                <input name="order" type="hidden" class="o_wsale_search_order_by" value="list_price asc"/>
              </form>
            </div>
          </div>
        </div>
        <a class="o_scroll_button mb-3 rounded-circle align-items-center justify-content-center\\
          mx-auto bg-primary" href="#" title="Scroll down to next section">
          <i class="fa fa-angle-down fa-3x"/>
        </a>
      </section>
      <section class="s_banner pt96 pb96 o_colored_level s_parallax_no_overflow_hidden"
        data-scroll-background-ratio="0" data-snippet="s_banner" data-name="Banner">
        <div class="container">
          <div class="row s_nb_column_fixed" data-original-title="" title=""
            aria-describedby="tooltip28849">
            <div class="col-lg-6 jumbotron rounded o_cc o_cc1 pt32 pb32 o_colored_level" data-name="Box">
              <form method="get" data-snippet="s_products_searchbar_input"
                class="o_wsale_products_searchbar_form s_wsale_products_searchbar_input"
                action="/shop" data-name="Products Search">
                <div role="search" class="input-group">
                  <input type="search" name="search" class="search-query form-control oe_search_box"
                    data-limit="5" data-display-description="true" data-display-price="true"
                    data-display-image="true" placeholder="Search..." autocomplete="off"/>
                  <div class="input-group-append">
                    <button type="submit" class="btn btn-primary oe_search_button" aria-label="Search"
                      title="Search">
                      <i class="fa fa-search">​</i>
                    </button>
                  </div>
                </div>
                <input name="order" type="hidden" class="o_wsale_search_order_by" value=""/>
              </form>
              <form method="get" data-snippet="s_products_searchbar_input"
                class="o_wsale_products_searchbar_form s_wsale_products_searchbar_input"
                action="/shop" data-name="Products Search">
                <div role="search" class="input-group">
                  <input type="search" name="search" class="search-query form-control oe_search_box"
                    data-limit="25" data-display-description="" data-display-price="true"
                    data-display-image="true" placeholder="Search..." autocomplete="off"/>
                  <div class="input-group-append">
                    <button type="submit" class="btn btn-primary oe_search_button" aria-label="Search"
                      title="Search">
                      <i class="fa fa-search">​</i>
                    </button>
                  </div>
                </div>
                <input name="order" type="hidden" class="o_wsale_search_order_by" value="name desc"/>
              </form>
              <h1>
                <br/>
              </h1>
            </div>
          </div>
        </div>
      </section>
    </div>
  </t>
</t>
        """
        view_ids = self.env["ir.ui.view"].create(
            {
                "name": "Product Searchbar Snippet Test",
                "type": "qweb",
                "key": "website_sale.product_searchbar_snippet_test",
                "website_id": self.env.ref("website.default_website").id,
                "arch": arch.replace("\\\n", ""),
            }
        )
        return {"view_id": view_ids.id}

    def check(self, init):
        view_id = self.env["ir.ui.view"].browse(init["view_id"])
        body = html.fromstring(view_id.arch, parser=utf8_parser)
        snippet_els = body.xpath("//section[@data-snippet='s_searchbar']")
        self.assertEqual(2, len(snippet_els))
        input_els = body.xpath("//form[@data-snippet='s_searchbar_input']//input[@type='search']")
        self.assertEqual(4, len(input_els))

        for el in input_els:
            search_type = el.get("data-search-type")
            self.assertEqual("products", search_type)

        # check first (section, defaults)
        el = input_els[0]
        limit = el.get("data-limit")
        self.assertEqual("5", limit)
        order_by = el.get("data-order-by")
        self.assertEqual("website_sequence asc", order_by)
        display_image = el.get("data-display-image", "")
        self.assertEqual("true", display_image)
        display_description = el.get("data-display-description", "")
        self.assertEqual("true", display_description)
        display_detail = el.get("data-display-detail", "")
        self.assertEqual("true", display_detail)

        # check second (section, options)
        el = input_els[1]
        limit = el.get("data-limit")
        self.assertEqual("15", limit)
        order_by = el.get("data-order-by")
        self.assertEqual("list_price asc", order_by)
        display_image = el.get("data-display-image", "")
        self.assertEqual("", display_image)
        display_description = el.get("data-display-description", "")
        self.assertEqual("", display_description)
        display_detail = el.get("data-display-detail", "")
        self.assertEqual("", display_detail)

        # check third (form only, defaults)
        el = input_els[2]
        limit = el.get("data-limit")
        self.assertEqual("5", limit)
        order_by = el.get("data-order-by")
        self.assertEqual("website_sequence asc", order_by)
        display_image = el.get("data-display-image", "")
        self.assertEqual("true", display_image)
        display_description = el.get("data-display-description", "")
        self.assertEqual("true", display_description)
        display_detail = el.get("data-display-detail", "")
        self.assertEqual("true", display_detail)

        # check fourth (form-only, options)
        el = input_els[3]
        limit = el.get("data-limit")
        self.assertEqual("25", limit)
        order_by = el.get("data-order-by")
        self.assertEqual("name desc", order_by)
        display_image = el.get("data-display-image", "")
        self.assertEqual("true", display_image)
        display_description = el.get("data-display-description", "")
        self.assertEqual("", display_description)
        display_detail = el.get("data-display-detail", "")
        self.assertEqual("true", display_detail)
