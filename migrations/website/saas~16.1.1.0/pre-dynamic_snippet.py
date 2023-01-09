# -*- coding: utf-8 -*-
import re
import sys
import uuid
from pathlib import Path

import odoo.upgrade.util.snippets as snip
from odoo.upgrade import util


def convert_dynamic(el):
    el_class_attr = el.get("class")
    classes = re.split(r"\s+", el_class_attr)
    initial_classes = classes.copy()
    if "d-none" in classes and "d-md-block" not in classes:
        classes.remove("d-none")
    if "o_dynamic_empty" not in classes:
        classes.append("o_dynamic_empty")
    if classes != initial_classes:
        el.set("class", " ".join(classes))
        return True
    return False


def migrate(cr, version):
    f = Path(__file__)
    f.relative_to(f.parent.parent.parent)

    # NOTE
    # `ProcessPoolExecutor.map` arguments needs to be pickleable
    # Functions can only be pickle if they are importable.
    # However, the current file is not importable due to the dash in the filename.
    # We should then put the executed function in its own importable file.
    name = f"_upgrade_{uuid.uuid4().hex}"
    mod = sys.modules[name] = util.import_script(str(f), name=name)

    snip.convert_html_content(
        cr,
        snip.html_selector_converter(mod.convert_dynamic, selector="//section[hasclass('s_dynamic')]"),
        where_column=r"~ '\ysection\y.+\ys_dynamic\y'",
    )
