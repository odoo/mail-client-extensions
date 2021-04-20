# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_event.country_events_list")
    util.remove_view(cr, "website_event.index_sidebar_country_event")
    util.remove_view(cr, "website_event.s_country_events")
