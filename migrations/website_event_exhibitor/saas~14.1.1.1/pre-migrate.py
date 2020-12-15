# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    # move sponsor model and fields from _track to _exhibitor
    util.move_model(cr, "event.sponsor", "website_event_track", "website_event_exhibitor", move_data=True)
    for suffix in {"manager", "public"}:
        util.rename_xmlid(cr, *eb(f"website_event_exhibitor.access_event_{{track_,}}sponsor_{suffix}"))

    util.move_model(cr, "event.sponsor.type", "website_event_track", "website_event_exhibitor", move_data=True)
    for suffix in {"manager", "public"}:
        util.rename_xmlid(cr, *eb(f"website_event_exhibitor.access_event_{{track_,}}sponsor_type_{suffix}"))

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

    # rename records
    util.rename_xmlid(cr, *eb("website_event_{track,exhibitor}.event_sponsor"), noupdate=False)
    util.rename_xmlid(cr, *eb("website_event_{track,exhibitor}.event_sponsor_type_view_tree"), noupdate=False)
    util.rename_xmlid(cr, *eb("website_event_{track,exhibitor}.event_sponsor_type_view_form"), noupdate=False)
    util.rename_xmlid(cr, *eb("website_event_{track,exhibitor}.event_sponsor_type_action"), noupdate=False)
    util.rename_xmlid(cr, *eb("website_event_{track,exhibitor}.menu_event_sponsor_type"), noupdate=False)
    util.rename_xmlid(cr, *eb("website_event_{track,exhibitor}.event_sponsor_action_from_event"), noupdate=False)

    views = """
        assets_frontend

        # force recreation of these views
        event_event_view_form

        event_sponsor_view_search
        event_sponsor_view_tree
        event_sponsor_view_kanban
        event_sponsor_view_form
    """
    for view in util.splitlines(views):
        util.remove_view(cr, f"website_event_exhibitor.{view}")
