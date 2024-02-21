# -*- coding: utf-8 -*-

import re

from odoo.upgrade.util import snippets


def replace_mobile_orders(el):
    orderedEls = el.xpath('.//*[hasclass("order-lg-0")]')
    if not len(orderedEls):
        return False
    for orderedEl in orderedEls:
        cls = orderedEl.attrib["class"]
        orderMatch = re.search(r"(?<!\S)order-([0-9]{1,2})(?!\S)", cls, flags=re.I)
        if orderMatch:
            old_style = orderedEl.attrib.get("style", "")
            orderedEl.attrib["style"] = f"order: {orderMatch.group(1)}; {old_style}"
            orderedEl.attrib["class"] = cls[: orderMatch.span()[0]] + cls[orderMatch.span()[1] :]
    return True


def migrate(cr, version):
    snippets.convert_html_content(
        cr,
        snippets.html_converter(replace_mobile_orders, selector="//*[hasclass('row')]"),
        where_column=r"~ '\yrow\y'",
    )
