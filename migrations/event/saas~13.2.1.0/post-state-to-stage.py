# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE event_event
           SET stage_id = CASE state WHEN 'confrim' THEN %s
                                     WHEN 'cancel' THEN %s
                                     WHEN 'done' THEN %s
                                     ELSE %s  -- when 'draft' or other
                           END
    """,
        [util.ref(cr, f"event.event_stage_{stage}") for stage in ["announced", "cancelled", "done", "new"]],
    )

    util.remove_column(cr, "event_event", "state")
