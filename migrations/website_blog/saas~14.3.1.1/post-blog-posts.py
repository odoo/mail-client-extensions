# -*- coding: utf-8 -*-

from lxml import etree, html

import odoo.upgrade.util.snippets as snip
from odoo.upgrade import util

utf8_parser = html.HTMLParser(encoding="utf-8")


def migrate(cr, version):
    # Blog posts snippet
    # -> For the views
    migrate_blog_posts_snippet(cr, "ir_ui_view", "arch_db")
    # -> For the HTML fields
    for table, column in snip.get_html_fields(cr):
        migrate_blog_posts_snippet(cr, table, column)
    # -> For the translations
    migrate_blog_posts_snippet(cr, "ir_translation", "value")


def migrate_blog_posts_snippet(cr, table, column):
    most_viewed_filter_id = "%s" % util.ref(cr, "website_blog.dynamic_filter_most_viewed_blog_posts")
    latest_filter_id = "%s" % util.ref(cr, "website_blog.dynamic_filter_latest_blog_posts")
    cr.execute(
        r"""
            SELECT id, {column}
              FROM {table}
             WHERE {column} ~ '\ys_latest_posts\y'
        """.format(
            table=table, column=column
        )
    )
    for res_id, body in cr.fetchall():
        body = html.fromstring(body, parser=utf8_parser)
        snippet_els = body.xpath("//section[hasclass('s_latest_posts')]")
        for el in snippet_els:
            row = el.xpath(".//div[hasclass('container')]/div[hasclass('row')]")[0]

            el.set("data-snippet", "s_blog_posts")
            el.set("data-number-of-elements", "3")
            el.set("data-number-of-elements-small-devices", "1")
            el.set("data-number-of-records", "3")
            # get id of blog post filter according to data-order
            old_order = row.get("data-order", "")
            filter_id = most_viewed_filter_id if "visits" in old_order else latest_filter_id
            el.set("data-filter-id", filter_id)
            # determine layout from old template
            row_classes = set(row.get("class", "").split(" "))
            template_xmlid = "website_blog.dynamic_filter_template_blog_post_big_picture"
            if "s_latest_posts_list" in row_classes:
                template_xmlid = "website_blog.dynamic_filter_template_blog_post_list"
            elif "s_latest_posts_horizontal" in row_classes:
                template_xmlid = "website_blog.dynamic_filter_template_blog_post_horizontal"
            elif "s_latest_posts_card" in row_classes:
                template_xmlid = "website_blog.dynamic_filter_template_blog_post_card"
            el.set("data-template-key", template_xmlid)
            blog_id = row.get("data-filter-by-blog-id", "-1")
            blog_id = "-1" if blog_id == "0" else blog_id
            el.set("data-filter-by-blog-id", blog_id)

            if "data-vcss" in el.attrib:
                del el.attrib["data-vcss"]

            classes = set(el.get("class", "").split(" "))
            classes.difference_update(
                [
                    "s_latest_posts",
                ]
            )
            layout_class = template_xmlid.replace("website_blog.dynamic_filter_template_", "s_")
            # keep existing effect from section/div.container/div.row
            effect_class = ""
            if "s_latest_posts_effect_marley" in row_classes:
                effect_class = "s_blog_posts_effect_marley"
            elif "s_latest_posts_effect_dexter" in row_classes:
                effect_class = "s_blog_posts_effect_dexter"
            elif "s_latest_posts_effect_chico" in row_classes:
                effect_class = "s_blog_posts_effect_chico"
            classes.update(
                [
                    "s_blog_posts",
                    "s_dynamic",
                    "s_dynamic_snippet_blog_posts",
                    layout_class,
                    effect_class,
                ]
            )
            el.set("class", " ".join(classes))

            old_container = el.xpath(".//div[hasclass('container')]")[0]
            new_container = html.fromstring(
                """
<div class="container o_not_editable">
    <div class="css_non_editable_mode_hidden">
        <div class="missing_option_warning alert alert-info rounded-0 fade show d-none d-print-none o_default_snippet_text">
            Your Dynamic Snippet will be displayed here...
            This message is displayed because you did not provided both a filter and a template to use.<br/>
        </div>
    </div>
    <div class="dynamic_snippet_template"/>
</div>
                """,
                parser=utf8_parser,
            )
            old_container.getparent().replace(old_container, new_container)

        if snippet_els:
            body = etree.tostring(body, encoding="unicode")
            cr.execute(f"UPDATE {table} SET {column} = %s WHERE id = %s", [body, res_id])
