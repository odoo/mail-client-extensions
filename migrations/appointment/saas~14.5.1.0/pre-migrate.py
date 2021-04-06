# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    cr.execute("ALTER TABLE website_calendar_type_country_rel RENAME TO appointment_type_country_rel")
    cr.execute("ALTER TABLE website_calendar_type_employee_rel RENAME TO appointment_type_employee_rel")

    # Move website related_field
    cr.execute(
        """
        SELECT name
        FROM ir_model_fields
        WHERE model in ('website.seo.metadata', 'website.published.mixin', 'website.cover_properties.mixin')
        AND name NOT IN ('id', 'create_uid', 'write_uid', 'create_date', 'write_date', '__lastupdate', 'display_name')
        """
    )
    for field in cr.fetchall():
        util.move_field_to_module(
            cr,
            "calendar.appointment.type",
            field[0],
            "appointment",
            "website_appointment",
        )

    # Rename and move views/template/rule
    # user_navbar_inherit_website_enterprise_inherit_website_appointment is
    # also moved to `website_appointment` in the next loop
    renames = [
        "appointment.user_navbar_inherit_website_enterprise_inherit_website_{calendar,appointment}",
        "appointment.calendar_event_view_search_inherit_{website_calendar,appointment}",
        "appointment.calendar_event_view_form_inherit_{website_calendar,appointment}",
        "appointment.{website_calendar,calendar_event_action}_report",
    ]
    for rename in renames:
        util.rename_xmlid(cr, *eb(rename))

    moves = [
        "{,website_}appointment.user_navbar_inherit_website_enterprise_inherit_website_appointment",
        "{,website_}appointment.calendar_appointment_type_rule_public",
        "{,website_}appointment.website_calendar_index",
        "{,website_}appointment.appointments_cards",
        "{,website_}appointment.appointments_cards_layout",
        "{,website_}appointment.appointments_list_layout",
        "{,website_}appointment.appointments_search_box",
        "{,website_}appointment.website_calendar_index_topbar",
        "{,website_}appointment.opt_appointments_list_cards",
        "{,website_}appointment.menu_appointment",
        "{,website_}appointment.website_appointment_type_menu",
    ]
    for move in moves:
        util.rename_xmlid(cr, *eb(move))

    util.create_column(cr, "calendar_appointment_type", "category", "varchar", default="website")
    util.create_column(cr, "calendar_appointment_slot", "slot_type", "varchar", default="recurring")
    util.create_column(cr, "calendar_appointment_slot", "start_datetime", "timestamp without time zone")
    util.create_column(cr, "calendar_appointment_slot", "end_datetime", "timestamp without time zone")
    util.create_column(cr, "calendar_appointment_slot", "allday", "boolean")
