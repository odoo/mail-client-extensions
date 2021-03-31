# -*- coding: utf-8 -*-

from lxml import etree, html

from odoo.upgrade import util

utf8_parser = html.HTMLParser(encoding="utf-8")


def migrate(cr, version):
    # Product recently viewed snippet
    # -> For the views
    migrate_product_recently_viewed_snippet(cr, "ir_ui_view", "arch_db")
    # -> For the HTML fields
    snip = util.import_script("web_editor/saas~13.2.1.0/snippets.py")
    for table, column in snip.get_html_fields(cr):
        migrate_product_recently_viewed_snippet(cr, table, column)
    # -> For the translations
    migrate_product_recently_viewed_snippet(cr, "ir_translation", "value")


def migrate_product_recently_viewed_snippet(cr, table, column):
    filter_id = "%s" % util.ref(cr, "website_sale.dynamic_filter_latest_viewed_products")
    cr.execute(
        r"""
            SELECT id, {column}
              FROM {table}
             WHERE {column} ~ '\ys_wsale_products_recently_viewed\y'
        """.format(
            table=table, column=column
        )
    )
    for res_id, body in cr.fetchall():
        body = html.fromstring(body, parser=utf8_parser)
        snippet_els = body.xpath("//section[hasclass('s_wsale_products_recently_viewed')]")
        for el in snippet_els:
            el.set("data-snippet", "s_dynamic_snippet_products")
            el.set("data-name", "Products")
            el.set("data-filter-id", filter_id)
            el.set("data-product-category-id", "all")
            el.set("data-template-key", "website_sale.dynamic_filter_template_product_product_add_to_cart")
            el.set("data-number-of-records", "16")
            el.set("data-number-of-elements", "4")
            el.set("data-number-of-elements-small-devices", "1")
            el.set("data-carousel-interval", "5000")

            if "data-invisible" in el.attrib:
                del el.attrib["data-invisible"]

            styles = el.get("style", "")
            el.set("style", styles.replace("min-height: 400px;", ""))

            classes = set(el.get("class", "").split(" "))
            classes.difference_update(
                [
                    "s_wsale_products_recently_viewed",
                    "o_snippet_invisible",
                ]
            )
            classes.update(
                [
                    "s_dynamic_snippet_products",
                    "s_dynamic",
                    "s_product_product_add_to_cart",
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
