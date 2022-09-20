# -*- coding: utf-8 -*-
import re

import odoo.upgrade.util.snippets as snip


def convert_device(el):
    el_class_attr = el.get("class", False)
    classes = re.split(r"\s+", el_class_attr)
    if any(class_name.startswith("d-md-") for class_name in classes):
        el.set("class", f"{el_class_attr} o_snippet_mobile_invisible")
        el.set("data-invisible", "1")
        return True

    return False


def migrate(cr, version):
    snip.convert_html_content(
        cr,
        snip.html_selector_converter(convert_device, selector="//*[hasclass('d-none')]"),
        where_column=r"~ '\yd-md-'",
    )
