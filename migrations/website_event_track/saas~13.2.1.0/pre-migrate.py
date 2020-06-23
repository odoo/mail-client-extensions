# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "event_track_stage", "color", "integer")
    cr.execute(
        """
        WITH colors AS (
            SELECT stage_id, (array_agg(color ORDER BY count desc))[1] as color
              FROM (
                SELECT stage_id, COALESCE(color, 0) as color, count(*)
                  FROM event_track
              GROUP BY stage_id, COALESCE(color, 0)
             ) x
          GROUP BY 1
        )
       UPDATE event_track_stage s
          SET color = c.color
         FROM colors c
        WHERE c.stage_id = s.id
    """
    )

    util.remove_column(cr, "event_track", "color")  # now related

    renames = {
        "event_sponsor_type": {"form", "tree"},
        "event_sponsor": {"tree", "search"},
    }

    for model, views in renames.items():
        for view in views:
            util.rename_xmlid(
                cr, f"website_event_track.view_{model}_{view}", f"website_event_track.{model}_view_{view}"
            )

    util.rename_xmlid(
        cr, "website_event_track.action_event_sponsor_type", "website_event_track.event_sponsor_type_action"
    )
    util.rename_xmlid(
        cr, "website_event_track.action_event_sponsor_from_event", "website_event_track.event_sponsor_action_from_event"
    )
