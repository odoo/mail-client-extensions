# -*- coding: utf-8 -*-
import re

from lxml import etree, html

import odoo.upgrade.util.snippets as snip
from odoo.upgrade import util

utf8_parser = html.HTMLParser(encoding="utf-8")


def remove_dnone_anchors(content):
    """
    Removes anchor elements that have the d-none class in social media blocks.

    :param content: the string from which elements must be removed
    :return: A tuple:
        1) A boolean which indicates if the content changed
        2) The updated content
    """
    # Wrap in <wrap> node before parsing to preserve external comments and
    # multi-root nodes
    content_el = html.fromstring(f"<wrap>{content}</wrap>", parser=utf8_parser)
    hasclass = "contains(concat(' ', normalize-space(@class), ' '), ' {} ')".format
    selector = f'//*[@data-snippet="s_social_media"]/a[{hasclass("d-none")}]'
    dnone_elements = content_el.xpath(selector)
    if not dnone_elements:
        return (False, content)
    for dnone_el in dnone_elements:
        dnone_el.getparent().remove(dnone_el)
    content = etree.tostring(content_el, encoding="unicode")
    content = re.sub(r"(^<wrap>|</wrap>$)", "", content.strip())
    return (True, content)


def migrate_social_media(cr, table, column, extra_where=""):
    if util.column_type(cr, table, column.strip('"')) == "jsonb":
        column_select = f"{column}->>'en_US'"
        column_value = "jsonb_build_object('en_US', %s)"
    else:
        column_select = column
        column_value = "%s"
    cr.execute(
        f"""
            SELECT id, {column_select}
            FROM {table}
            WHERE {column_select} LIKE '%s_social_media%d-none%'
            {extra_where}
        """
    )
    for id, content in cr.fetchall():
        content = re.sub(r"^<\?xml .+\?>\s*", "", content.strip())
        updated, new_content = remove_dnone_anchors(content)
        if not updated:
            continue
        cr.execute(
            f"""
                UPDATE {table}
                SET {column} = {column_value}
                WHERE id = %s
            """,
            [new_content, id],
        )


def migrate(cr, version):
    """
    Deletes the hidden links that are in a social_media block from website pages
    and from HTML fields.
    """
    migrate_social_media(cr, "ir_ui_view", "arch_db", "AND type = 'qweb'")
    for table, column in snip.get_html_fields(cr):
        migrate_social_media(cr, table, column)
