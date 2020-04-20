# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "event.type", "default_registration_min")
    util.remove_field(cr, "event.type", "is_online")
    util.rename_field(cr, "event.type", "default_registration_max", "seats_max")
    util.remove_field(cr, "event.event", "seats_min")
    util.remove_field(cr, "event.event", "is_online")
    util.create_column(cr, "event_event", "seats_limited", "boolean")
    cr.execute(
        """
        UPDATE event_event AS event
        SET seats_limited = (event.seats_availability = 'limited')
    """
    )
    util.remove_field(cr, "event.event", "seats_availability")

    if util.table_exists(cr, "event_type_ticket"):
        util.create_column(cr, "event_type_ticket", "seats_limited", "boolean")
        cr.execute(
            """
            UPDATE event_type_ticket AS ticket
            SET seats_limited = (ticket.seats_availability = 'limited')
        """
        )
        util.remove_field(cr, "event.type.ticket", "seats_availability")

        util.create_column(cr, "event_event_ticket", "seats_limited", "boolean")
        cr.execute(
            """
            UPDATE event_event_ticket AS ticket
            SET seats_limited = (ticket.seats_availability = 'limited')
        """
        )
        util.remove_field(cr, "event.event.ticket", "seats_availability")

    util.delete_unused(cr, "event.event_type_data_physical")
    util.rename_xmlid(cr, "website_event_track.event_type_data_tracks", "event.event_type_data_conference")

    util.remove_field(cr, "event.registration", "origin")
    for old_name in ["campaign_id", "source_id", "medium_id"]:
        util.move_field_to_module(cr, "event.registration", old_name, "event_sale", "event")
        util.rename_field(cr, "event.registration", old_name, f"utm_{old_name}")

    if util.table_exists(cr, "event_tag"):
        # This model existed in old versions (introduced in (7.)saas~3, removed in (8.)saas~6)
        # However, the upgrade script for saas~6 is ... minimal and doesn't clean the database
        util.move_model(cr, "event.tag", "website_event_track", "event", move_data=True)
    else:
        cr.execute(
            """
                CREATE TABLE event_tag (
                    id SERIAL PRIMARY KEY,
                    create_uid INTEGER,
                    create_date timestamp,
                    write_uid INTEGER,
                    write_date timestamp,
                    name varchar
                )
            """
        )

    m2m = "event_event_event_tag_rel"
    if util.table_exists(cr, m2m):
        util.fixup_m2m(cr, m2m, "event_event", "event_tag")
    else:
        util.create_m2m(cr, m2m, "event_event", "event_tag")
