# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # move sponsor model and fields from _track to _exhibitor
    util.move_model(cr, "event.sponsor", "website_event_track", "website_event_exhibitor", move_data=True)
    util.move_model(cr, "event.sponsor.type", "website_event_track", "website_event_exhibitor", move_data=True)
    util.move_field_to_module(cr, "event.event", "sponsor_ids", "website_event_track", "website_event_exhibitor")
    util.move_field_to_module(cr, "event.event", "sponsor_count", "website_event_track", "website_event_exhibitor")

    # migrate from is_exhibitor (defined in website_event_track_exhibitor)
    # to exhibitor_type selection. Do it only if column exists aka if module
    # was installed before migrating (as migrating could install website_event_exhibitor
    # if website_event_track was installed).
    util.create_column(cr, "event_sponsor", "exhibitor_type", "varchar", default="sponsor")
    if util.column_exists(cr, "event_sponsor", "is_exhibitor"):
        cr.execute(
            """
            UPDATE event_sponsor
               SET exhibitor_type = CASE WHEN chat_room_id IS NOT NULL THEN 'online'
                                         ELSE 'exhibitor'
                                    END
             WHERE is_exhibitor = true
        """
        )
        util.remove_field(cr, "event.sponsor", "is_exhibitor")
