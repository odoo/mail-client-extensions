# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "event.type", "default_registration_min")
    util.remove_field(cr, "event.event", "seats_min")

    util.delete_unused(cr, "event.event_type_data_physical")
    util.rename_xmlid(cr, "website_event_track.event_type_data_tracks", "event.event_type_data_conference")
    util.rename_field(cr, "event.type", "default_registration_max", "seats_max")

    util.remove_field(cr, "event.registration", "origin")
    for old_name in ["campaign_id", "source_id", "medium_id"]:
        util.move_field_to_module(cr, "event.registration", old_name, "event_sale", "event")
        util.rename_field(cr, "event.registration", old_name, f"utm_{old_name}")
