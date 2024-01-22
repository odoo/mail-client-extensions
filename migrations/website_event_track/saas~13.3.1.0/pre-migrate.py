# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_event_track.event_track_social")
    util.remove_record(cr, "website_event_track.access_event_location_manager")

    # Allow archiving of sponsors and get sponsor URL from partner
    util.create_column(cr, "event_sponsor", "active", "boolean", default=True)

    util.fixup_m2m(cr, "event_track_event_track_tag_rel", "event_track", "event_track_tag")

    # Data (changed by odoo/odoo#53944)
    eb = util.expand_braces
    # Don't change label of existing tags (demo data)
    util.rename_xmlid(cr, *eb("website_event_track.event_track_tag{1,_technical}"), noupdate=True)
    util.rename_xmlid(cr, *eb("website_event_track.event_track_tag{2,_business}"), noupdate=True)
    util.rename_xmlid(cr, *eb("website_event_track.event_track_tag{3,11}"), noupdate=True)
    util.rename_xmlid(cr, *eb("website_event_track.event_track_tag{4,12}"), noupdate=True)

    # event-online requirements
    util.update_record_from_xml(cr, "website_event_track.event_track_proposal")
    if not util.version_gte("saas~13.5"):
        util.update_record_from_xml(cr, "website_event_track.agenda")
        util.update_record_from_xml(cr, "website_event_track.track_view")
