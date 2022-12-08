# -*- coding: utf-8 -*-
import re

from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    for t in "anelusia kea loftspace monglia".split():
        util.remove_view(cr, "theme_%s.font_size" % t)

    # adapt templates to "blog-style" snippet removed option
    bad_pattern = "//div[@data-js='blog-style']"
    cr.execute(
        """
        SELECT id
          FROM ir_ui_view
         WHERE arch_db ~ %s
    """,
        [re.escape('expr="%s"' % bad_pattern)],
    )
    for (vid,) in cr.fetchall():
        with util.edit_view(cr, view_id=vid) as arch:
            for node in arch.xpath('//xpath[@expr="%s"]' % bad_pattern):
                if node.attrib.get("position") == "attributes":
                    node.getparent().remove(node)
                else:
                    node.attrib["expr"] = "//div[@data-js='background']"
                    node.attrib["position"] = "before"
