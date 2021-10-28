# -*- coding: utf-8 -*-

from lxml import etree, html

import odoo.upgrade.util.snippets as snip

utf8_parser = html.HTMLParser(encoding="utf-8")


def migrate(cr, version):
    # Blog posts snippet
    # -> For the views
    migrate_products_searchbar_snippet(cr, "ir_ui_view", "arch_db")
    # -> For the HTML fields
    for table, column in snip.get_html_fields(cr):
        migrate_products_searchbar_snippet(cr, table, column)
    # -> For the translations
    migrate_products_searchbar_snippet(cr, "ir_translation", "value")


def migrate_products_searchbar_snippet(cr, table, column):
    cr.execute(
        r"""
            SELECT id, {column}
              FROM {table}
             WHERE {column} ~ '\ys_products_searchbar_input\y'
        """.format(
            table=table, column=column
        )
    )
    for res_id, body in cr.fetchall():
        body = html.fromstring(body, parser=utf8_parser)
        # 1. sections
        snippet_els = body.xpath("//section[hasclass('s_wsale_products_searchbar')]")
        for el in snippet_els:
            el.set("data-snippet", "s_searchbar")
            el.set("data-name", "Search")

            classes = set(el.get("class", "").split(" "))
            classes.difference_update(
                [
                    "s_wsale_products_searchbar",
                ]
            )
            classes.update(
                [
                    "s_searchbar",
                ]
            )
            el.set("class", " ".join(classes))

            if "data-vxml" in el.attrib:
                del el.attrib["data-vxml"]

        # 2. forms (possibly without encapsulating section)
        form_els = body.xpath("//form[hasclass('o_wsale_products_searchbar_form')]")
        for el in form_els:
            el.set("data-snippet", "s_searchbar_input")
            if "data-name" in el.attrib:
                el.set("data-name", "Search")

            classes = set(el.get("class", "").split(" "))
            classes.difference_update(
                [
                    "o_wsale_products_searchbar_form",
                    "s_wsale_products_searchbar_input",
                ]
            )
            classes.update(
                [
                    "o_searchbar_form",
                    "s_searchbar_input",
                ]
            )
            el.set("class", " ".join(classes))

            # 2.1. form's order input
            old_order = "website_sequence asc"
            for order_input in el.xpath(".//input[hasclass('o_wsale_search_order_by')]"):
                old_order = order_input.get("value")
                if not old_order:
                    old_order = "website_sequence asc"
                order_input.set("value", old_order)

                order_classes = set(order_input.get("class", "").split(" "))
                order_classes.difference_update(
                    [
                        "o_wsale_search_order_by",
                    ]
                )
                order_classes.update(
                    [
                        "o_search_order_by",
                    ]
                )
                order_input.set("class", " ".join(order_classes))

            # 2.2. form's search input
            for search_input in el.xpath(".//input[hasclass('oe_search_box')]"):
                search_input.set("data-search-type", "products")
                search_input.set("data-order-by", old_order)
                search_input.set("data-display-extra-link", "true")
                if "data-display-price" in search_input.attrib:
                    search_input.set("data-display-detail", search_input.get("data-display-price"))
                    del search_input.attrib["data-display-price"]

        if snippet_els or form_els:
            body = etree.tostring(body, encoding="unicode")
            cr.execute(f"UPDATE {table} SET {column} = %s WHERE id = %s", [body, res_id])
