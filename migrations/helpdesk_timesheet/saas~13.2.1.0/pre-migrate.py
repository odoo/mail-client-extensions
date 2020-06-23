# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "helpdesk_team", "timesheet_timer", "boolean")
    cr.execute("UPDATE helpdesk_team SET timesheet_timer = use_helpdesk_timesheet")

    util.create_column(cr, "project_project", "allow_timesheet_timer", "boolean")
    cr.execute(
        """
        WITH ptt AS (
            SELECT p.id, bool_or(t.timesheet_timer) as timer
              FROM project_project p
         LEFT JOIN helpdesk_team t ON t.project_id = p.id
          GROUP BY p.id
        )
        UPDATE project_project p
           SET allow_timesheet_timer = ptt.timer
          FROM ptt
         WHERE ptt.id = p.id
    """
    )
