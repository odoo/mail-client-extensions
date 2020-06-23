# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # Removal of twitter hashtag field could lead to crash if not updated
    util.force_noupdate(cr, "website_event.event_description_full", False)

    util.remove_view(cr, "website_event.event_category")
    util.remove_view(cr, "website_event.index_sidebar_categories")
