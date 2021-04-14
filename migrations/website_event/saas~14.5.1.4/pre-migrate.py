# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "event_event", "introduction_menu", "boolean", default=False)
    util.create_column(cr, "event_event", "location_menu", "boolean", default=False)
    util.create_column(cr, "event_event", "register_menu", "boolean", default=False)
    util.remove_view(cr, "website_event.event_category_tag")
