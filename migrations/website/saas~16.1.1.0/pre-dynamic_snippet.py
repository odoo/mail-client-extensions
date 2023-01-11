# -*- coding: utf-8 -*-
import re

import odoo.upgrade.util.snippets as snip


def convert_dynamic(el):
    el_class_attr = el.get("class")
    classes = re.split(r"\s+", el_class_attr)
    initial_classes = classes.copy()
    regex = re.compile(r"^d-(md|lg)-(?!none)")
    if "d-none" in classes and not any(regex.match(c) for c in classes):
        classes.remove("d-none")
    if "o_dynamic_empty" not in classes:
        classes.append("o_dynamic_empty")
    if classes != initial_classes:
        el.set("class", " ".join(classes))
        return True
    return False


def migrate(cr, version):
    snip.convert_html_content(
        cr,
        snip.html_converter(convert_dynamic, selector="//section[hasclass('s_dynamic')]"),
        where_column=r"~ '\ysection\y.+\ys_dynamic\y'",
    )
