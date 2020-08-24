# -*- coding: utf-8 -*-
import re
from lxml import etree, html
from odoo.upgrade import util

utf8_parser = html.HTMLParser(encoding="utf-8")


def migrate_parallax(cr, table, column):
    bg_image_regex = r"background-image\s*:\s*(url\(.+\))\s*(?:;|$)"
    bg_color_regex = r"background-color\s*:\s*([^;]+)\s*(?:;|$)"
    bg_color_class_regex = r"\b(bg-(?:black|white)-\d{2})\b"
    HIDDEN_CLASS = "s_parallax_no_overflow_hidden"
    FIXED_CLASS = "s_parallax_is_fixed"

    cr.execute(
        r"""
            SELECT id, {column}
              FROM {table}
             WHERE {column} ~ '\yparallax\y'
        """.format(
            table=table, column=column
        )
    )
    for res_id, body in cr.fetchall():
        body = html.fromstring(body, parser=utf8_parser)
        changed = False
        parallax_els = body.xpath("//*[hasclass('parallax')]")
        for el in parallax_els:
            # 1. Get the background image of the snippet if any and remove it:
            #    it should be on the parallax element
            styles = el.get("style", "")
            bg_image_match = re.search(bg_image_regex, styles)
            if bg_image_match:
                styles = re.sub(bg_image_regex, "", styles)
                el.set("style", styles)
                changed = True

            # 2. Set appropriate classes according to parallax speed
            classes = el.get("class", "").split(" ")
            speed = el.get("data-scroll-background-ratio")
            has_hidden_class = HIDDEN_CLASS in classes
            has_fixed_class = FIXED_CLASS in classes
            if speed == "0" or speed == "1":
                if not has_hidden_class:
                    classes.append(HIDDEN_CLASS)
                    changed = True
            elif has_hidden_class:
                classes.remove(HIDDEN_CLASS)
                changed = True
            if speed == "1":
                if not has_fixed_class:
                    classes.append(FIXED_CLASS)
                    changed = True
            elif has_fixed_class:
                classes.remove(FIXED_CLASS)
                changed = True
            el.set("class", " ".join(classes))

            # 3. Some databases may have snippets who failed to save the
            #    s_parallax_bg element, so we have to create it.
            bg_el = None
            children = list(el)
            for child in children:
                if "s_parallax_bg" in child.get("class", "").split(" "):
                    bg_el = child
                    break
            if bg_el is None:
                bg_el = etree.Element("span")
                bg_el.set("class", "s_parallax_bg oe_img_bg")
                if bg_image_match is not None:
                    bg_el.set("style", f"background-image: {bg_image_match[1]};")
                el.insert(0, bg_el)
                changed = True

            # 4. The parallax color filter is now an independant generic color
            #    filter; the related element has to be created.
            classes = el.get("class", "")
            bg_color_class_match = re.search(bg_color_class_regex, classes)
            bg_color_match = re.search(bg_color_regex, styles)
            if bg_color_class_match is not None or bg_color_match is not None:
                filter_el = etree.Element("div")
                color_class = bg_color_class_match is not None and bg_color_class_match[1] or ""
                filter_el.set("class", f"o_we_bg_filter {color_class}")
                if bg_color_match is not None:
                    filter_el.set("style", f"background-color: {bg_color_match[1]};")
                el.insert(el.index(bg_el) + 1, filter_el)
                changed = True
        if changed:
            body = etree.tostring(body, encoding="unicode")
            cr.execute(f"UPDATE {table} SET {column} = %s WHERE id = %s", [body, res_id])


def migrate(cr, version):
    util.create_column(cr, "website_page", "header_visible", "boolean", default=True)
    util.create_column(cr, "website_page", "footer_visible", "boolean", default=True)

    util.remove_view(cr, "website.s_color_blocks_2_options")
    util.remove_view(cr, "website.s_masonry_block_options")
    util.remove_view(cr, "website.s_text_highlight_options")
    util.remove_view(cr, "website.option_custom_body_image")
    util.remove_view(cr, "website.option_custom_body_pattern")
    util.rename_xmlid(cr, "website.snippet_options_border", "website.snippet_options_border_widgets")
    util.rename_xmlid(cr, "website.snippet_options_shadow", "website.snippet_options_shadow_widgets")

    # Reattach the base and COWed views for the cookie bar to the right
    # inherited view. The cookie bar template was
    # inheriting the footer_custom view before so we have to remove the COWed
    # ones before moving on the footer template migration. By simplicity, just
    # remove the view before it is re-created correctly when upgrading website.
    cr.execute("SELECT website_id, id FROM ir_ui_view WHERE key = 'website.layout'")
    layout_views = dict(cr.fetchall())
    cr.execute("SELECT id, website_id FROM ir_ui_view WHERE key = 'website.cookies_bar'")
    for (view_id, website_id) in cr.fetchall():
        inherit_id = layout_views.get(website_id, layout_views.get(None))
        cr.execute(
            "UPDATE ir_ui_view SET inherit_id = %s WHERE id = %s", [inherit_id, view_id],
        )
    # Note: this is done in website and not website_twitter_wall as the
    # COWed views need to be removed before moving on the footer template
    # migration.
    util.remove_view(cr, "website_twitter_wall.twitter_wall_footer_custom")

    # Parallax feature
    # -> For the views
    migrate_parallax(cr, "ir_ui_view", "arch_db")
    # -> For the HTML fields
    snip = util.import_script("web_editor/saas~13.2.1.0/snippets.py")
    for table, column in snip.get_html_fields(cr):
        migrate_parallax(cr, table, column)
