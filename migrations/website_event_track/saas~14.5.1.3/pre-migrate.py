# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "event_track_stage", "description", "text")
    util.create_column(cr, "event_track_stage", "legend_blocked", "varchar", default="Blocked")
    util.create_column(cr, "event_track_stage", "legend_done", "varchar", default="Ready for Next Stage")
    util.create_column(cr, "event_track_stage", "legend_normal", "varchar", default="In Progress")
    util.rename_field(cr, "event.track.stage", "is_accepted", "is_visible_in_agenda")
    util.rename_field(cr, "event.track.stage", "is_done", "is_fully_accessible")

    util.remove_field(cr, "event.track", "is_accepted")
    util.create_column(cr, "event_track", "kanban_state_label", "varchar")
    # pre compute kanban state label; as fields are new, let us skip translations
    # as anyway future changes will use right language in tracking
    cr.execute(
        """
        UPDATE event_track
           SET kanban_state_label = CASE WHEN kanban_state = 'done' THEN 'Ready for Next Stage'
                                         WHEN kanban_state = 'blocked' THEN 'Blocked'
                                         ELSE 'In Progress'
                                         END
        """
    )

    util.remove_view(cr, "website_event_track.tracks_cards_track")
    util.remove_view(cr, "website_event_track.event_track_proposal_success")
