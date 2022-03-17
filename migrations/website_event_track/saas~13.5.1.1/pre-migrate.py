# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    util.create_column(cr, "event_sponsor_type", "display_ribbon_style", "varchar", default="no_ribbon")

    for f in {"name", "email", "phone", "mobile"}:
        util.create_column(cr, "event_sponsor", f, "varchar")
    util.parallel_execute(
        cr,
        util.explode_query(
            cr,
            """
        UPDATE event_sponsor s
           SET name = COALESCE(s.name, p.name),
               email = COALESCE(s.email, p.email),
               phone = COALESCE(s.phone, p.phone),
               mobile = COALESCE(s.mobile, p.mobile)
          FROM res_partner p
         WHERE p.id = s.partner_id
    """,
            alias="s",
        ),
    )

    util.create_column(cr, "event_track", "wishlisted_by_default", "boolean", default=False)
    util.create_column(cr, "event_track", "website_cta", "boolean", default=False)
    util.create_column(cr, "event_track", "website_cta_title", "varchar")
    util.create_column(cr, "event_track", "website_cta_url", "varchar")
    util.create_column(cr, "event_track", "website_cta_delay", "integer")

    util.create_column(cr, "event_track_stage", "is_accepted", "boolean", default=False)

    util.create_column(cr, "event_track_tag", "category_id", "integer")
    if util.create_column(cr, "event_track_tag", "sequence", "integer"):
        cr.execute(
            """
                WITH seq AS (
                    SELECT id, row_number() OVER (ORDER BY name) as seq
                      FROM event_track_tag
                )
                UPDATE event_track_tag t
                   SET sequence = seq.seq
                  FROM seq
                 WHERE seq.id = t.id
            """
        )

    # data
    gone_views = """
        # from merged modules
        event_type_view_form
        event_track_tag_view_list
        event_track_tag_view_form
        event_track_view_form
        event_track_view_tree
        event_track_view_search

        # from self
        agenda
        tracks
        tracks_filter
        tracks_whishlist
        track_view
        track_view_whishlist
    """
    for view in util.splitlines(gone_views):
        util.remove_view(cr, f"website_event_track.{view}")

    util.rename_xmlid(cr, *eb("website_event_track.{,pwa_}offline"))

    util.rename_xmlid(cr, "website_event_track.view_event_form", "website_event_track.event_event_view_form")
    util.rename_xmlid(
        cr,
        "website_event_track.event_event_view_list_inherit_website_event_track",
        "website_event_track.event_event_view_list",
    )
