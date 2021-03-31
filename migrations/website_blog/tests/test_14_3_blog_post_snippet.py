# -*- coding: utf-8 -*-

from lxml import html

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version

utf8_parser = html.HTMLParser(encoding="utf-8")


@change_version("14.3")
class TestBlogPostSnippet(UpgradeCase):
    def prepare(self):
        arch = """
<t name="Blog Snippet Test" t-name="website_blog.blog_snippet_test">
  <t t-call="website.layout">
    <t t-set="pageName" t-value="'blog snippet test'"/>
    <div id="wrap" class="oe_structure oe_empty">
      <section class="s_latest_posts pt16 pb16 o_colored_level" data-vcss="001"
        data-snippet="s_latest_posts" data-name="Blog Posts">
        <div class="container">
          <div class="row s_col_no_bgcolor s_nb_column_fixed js_get_posts s_latest_posts_big_picture\\
            s_latest_posts_effect_marley"
            data-loading="true" data-template="website_blog.s_latest_posts_big_picture_template"
            data-filter-by-blog-id="0" data-order="published_date desc"/>
        </div>
      </section>
      <section class="s_latest_posts pt16 pb16 o_colored_level o_cc o_cc3 oe_img_bg\\
        o_bg_img_center o_half_screen_height"
        data-vcss="001" data-snippet="s_latest_posts" data-name="Blog Posts"
        style="background-image: url('/website_blog/static/src/img/blog_1.jpeg'); position: relative;"
        data-oe-shape-data="{'shape':'web_editor/Origins/01','colors':{'c2':'#EA93D3','c5':'#383E45'},\\
          'flip':['x','y']}"
        data-original-id="1963" data-original-src="/website_blog/static/src/img/blog_1.jpeg"
        data-mimetype="image/jpeg" data-resize-width="1920">
        <div class="o_we_bg_filter" style="background-color: rgba(243, 62, 62, 0.5) !important;"/>
        <div class="o_we_shape o_web_editor_Origins_01" style="background-image: url(\\
          '/web_editor/shape/web_editor/Origins/01.svg?c2=%23EA93D3&amp;c5=%23383E45&amp;flip=xy');\\
          background-position: 50% 0%;"/>
        <div class="container">
          <div class="row s_col_no_bgcolor s_nb_column_fixed js_get_posts\\
            s_latest_posts_effect_marley s_latest_posts_list"
            data-loading="true" data-template="website_blog.s_latest_posts_list_template"
            data-filter-by-blog-id="2" data-order="visits desc"/>
        </div>
        <a class="o_scroll_button mb-3 rounded-circle align-items-center justify-content-center\\
          mx-auto bg-primary"
          href="#" title="Scroll down to next section">
          <i class="fa fa-angle-down fa-3x"/>
        </a>
      </section>
    </div>
  </t>
</t>
        """
        view_ids = self.env["ir.ui.view"].create(
            {
                "name": "Blog Snippet Test",
                "type": "qweb",
                "key": "website_blog.blog_snippet_test",
                "website_id": self.env.ref("website.default_website").id,
                "arch": arch.replace("\\\n", ""),
            }
        )
        return {"view_id": view_ids.id}

    def check(self, init):
        view_id = self.env["ir.ui.view"].browse(init["view_id"])
        body = html.fromstring(view_id.arch, parser=utf8_parser)
        snippet_els = body.xpath("//section[@data-snippet='s_blog_posts']")
        self.assertEqual(2, len(snippet_els))

        for el in snippet_els:
            dynamic_snippet_template = el.xpath(".//div[hasclass('dynamic_snippet_template')]")
            self.assertEqual(1, len(dynamic_snippet_template))

        # check first
        el = snippet_els[0]
        filter_id = self.env["website.snippet.filter"].browse(int(el.get("data-filter-id")))
        self.assertEqual("Latest Blog Posts", filter_id.name)
        template_key = el.get("data-template-key")
        self.assertEqual("website_blog.dynamic_filter_template_blog_post_big_picture", template_key)
        blog_id = int(el.get("data-filter-by-blog-id"))
        self.assertEqual(-1, blog_id)

        # check second
        el = snippet_els[1]
        filter_id = self.env["website.snippet.filter"].browse(int(el.get("data-filter-id")))
        self.assertEqual("Most Viewed Blog Posts", filter_id.name)
        template_key = el.get("data-template-key")
        self.assertEqual("website_blog.dynamic_filter_template_blog_post_list", template_key)
        blog_id = int(el.get("data-filter-by-blog-id"))
        self.assertEqual(2, blog_id)
