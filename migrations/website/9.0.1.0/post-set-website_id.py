# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # assign default website to manually modified views
    for name in ["homepage", "contactus", "aboutus"]:
        xmlid = "website." + name
        if util.is_changed(cr, xmlid):
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
