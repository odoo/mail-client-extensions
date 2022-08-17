# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # assign default website to manually modified views
    xmlids = ["website.{}".format(name) for name in "homepage contactus aboutus".split()]
    to_update = set(xmlids)
    for xmlid in xmlids:
        util.if_unchanged(cr, xmlid, lambda _, x: to_update.remove(x))
    for xmlid in to_update:
        cr.execute(
            """
            UPDATE ir_ui_view
               SET website_id = %s,
                   key = %s
             WHERE id = %s
               AND website_id IS NULL
            """,
            [
                util.ref(cr, "website.default_website"),
                xmlid,
                util.ref(cr, xmlid),
            ],
        )
