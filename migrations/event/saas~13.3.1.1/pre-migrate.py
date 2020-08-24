# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "event.type", "use_hashtag")
    util.remove_field(cr, "event.type", "default_hashtag")
    util.remove_field(cr, "event.type", "default_registration_min")
    util.remove_field(cr, "event.type", "is_online")
    util.rename_field(cr, "event.type", "default_registration_max", "seats_max")

    util.remove_field(cr, "event.event", "twitter_hashtag")
    util.remove_field(cr, "event.event", "seats_min")
    util.remove_field(cr, "event.event", "is_online")

    for model in ["event.event", "event.event.ticket", "event.type.ticket"]:
        # NOTE: we must process `event.event.ticket` before `event.type.ticket`.
        #       When upgrading from `saas~13.2`, the former inherit from the latter, thus removing
        #       the field from the latter will also remove it from the former, forbidding the UPDATE.
        table = util.table_of_model(cr, model)
        if not util.table_exists(cr, table):
            continue
        util.create_column(cr, table, "seats_limited", "boolean")
        cr.execute(f"UPDATE {table} SET seats_limited = (seats_availability = 'limited')")
        util.remove_field(cr, model, "seats_availability")

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

    util.rename_xmlid(cr, "website_event.event_category", "website_event.event_category_tag")
    util.force_noupdate(cr, 'website_event.event_category_tag', False)

    util.if_unchanged(cr, "event.event_subscription", util.update_record_from_xml)
    util.if_unchanged(cr, "event.event_reminder", util.update_record_from_xml)

    # ensure rule for acls update
    util.force_noupdate(cr, "event.access_event_registration_all", noupdate=False)
    util.force_noupdate(cr, "event.access_event_tag", noupdate=False)
    util.remove_record(cr, "event.event_registration_portal")
