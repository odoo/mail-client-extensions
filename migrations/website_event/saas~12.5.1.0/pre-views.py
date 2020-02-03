# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    def view_active(xid):
        cr.execute(
            """
            SELECT v.active
              FROM ir_model_data d
              JOIN ir_ui_view v ON d.model = 'ir.ui.view' AND d.res_id = v.id
             WHERE d.module = 'website_event'
               AND d.name = %s
        """,
            [xid],
        )
        return bool(cr.fetchone()[0]) if cr.rowcount else False

    util.ENVIRON["s125_website_event_options"] = {
        "photos": view_active("event_right_photos"),
        "quotes": view_active("event_right_quotes"),
        "country": view_active("event_right_country_event"),
    }

    views = util.splitlines(
        """
        event_right_column
        event_right_photos
        event_right_quotes
        event_right_country_event

        event_left_column

        country_events
        brand_promotion
    """
    )
    for view in views:
        util.remove_view(cr, "website_event." + view)

    views = util.splitlines("""
        # snippets
            s_country_events
            country_events_list
        # Filters
            event_time
            event_category
            event_location
        # templates
            template_location
            template_intro

        layout
        event_details
        event_description_full
        registration_template
        ticket
        registration_attendee_details
        registration_complete

        # backend views
            event_event_view_form_inherit_website
            event_event_view_list_inherit_website

    """)
    for view in views:
        util.force_noupdate(cr, "website_event." + view, noupdate=False)
