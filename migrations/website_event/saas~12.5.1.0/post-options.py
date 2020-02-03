# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):

    options = util.ENVIRON["s125_website_event_options"]

    def active_view(xid, option):
        vid = util.ref(cr, "website_event." + xid)
        active = options[option] if isinstance(option, str) else option
        cr.execute(
            """
            UPDATE ir_ui_view
               SET active = %s
             WHERE id = %s
        """,
            [active, vid],
        )

    active_view("index_sidebar_photos", "photos")
    active_view("index_sidebar_quotes", "quotes")
    active_view("index_sidebar_country_event", "country")
