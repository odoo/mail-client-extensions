# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_event.event_category")
    util.remove_view(cr, "website_event.index_sidebar_categories")

    # event-online requirements
    util.update_record_from_xml(cr, "website_event.layout")
    util.update_record_from_xml(cr, "website_event.events_list")
    util.update_record_from_xml(cr, "website_event.index_topbar")
    util.update_record_from_xml(cr, "website_event.events_list")
    util.update_record_from_xml(cr, "website_event.event_description_full")
    util.update_record_from_xml(cr, "website_event.registration_template")
    util.update_record_from_xml(cr, "website_event.registration_complete")
    util.update_record_from_xml(cr, "website_event.template_intro")
