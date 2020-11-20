# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.upgrade import util


def migrate(cr, version):
    # Clean the ACLs XMLID
    acl_name_changes = {
        "access_event_track__public": "event_track",
        "access_event_track_tag_public": "event_track_tag",
        "access_event_track_location_public": "event_track_location",
        "access_event_track_sponsor_type_manager": "event_sponsor_type_manager",
        "access_event_track_sponsor_type_public": "event_sponsor_type",
        "access_event_track_sponsor_manager": "event_sponsor_manager",
        "access_event_track_sponsor_public": "event_sponsor",
        "access_event_track_stage_all": "event_track_stage",
        "access_event_track_stage_event_manager": "event_track_stage_manager",
        "event_track_visitor_access_all": "event_track_visitor",
        "event_track_visitor_access_manager": "event_track_visitor_manager",
        "event_track_tag_category_access_public": "event_track_tag_category",
        "event_track_tag_category_access_manager": "event_track_tag_category_manager",
    }
    for old_name, new_name in acl_name_changes.items():
        util.rename_xmlid(cr, f"website_event_track.{old_name}", f"website_event_track.access_{new_name}")

    # Remove ACLs
    util.remove_record(cr, "website_event_track.access_event_track_tag_category_manager")
