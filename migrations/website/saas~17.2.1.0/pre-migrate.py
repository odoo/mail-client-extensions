import re

from lxml import html

from odoo.upgrade.util import snippets
from odoo.upgrade.util.convert_bootstrap import innerxml


def add_template_in_embed_code(el):
    if el.xpath('.//template[hasclass("s_embed_code_saved")]'):
        return False
    embedded_code = el.xpath('.//div[hasclass("s_embed_code_embedded")]')[0]
    code = innerxml(embedded_code, is_html=True)
    template = """<template class="s_embed_code_saved">%s</template>""" % code
    el.insert(0, html.fromstring(template, parser=html.HTMLParser(encoding="utf-8")))
    return True


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
    snippets.convert_html_content(
        cr,
        snippets.html_converter(add_template_in_embed_code, selector="//*[@data-snippet='s_embed_code']"),
        where_column=r"~ '\ys_embed_code\y'",
    )
