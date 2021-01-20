# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT ticket.id
          FROM helpdesk_ticket ticket
          JOIN helpdesk_team team ON ticket.team_id = team.id
         WHERE team.use_helpdesk_timesheet IS TRUE
        """
    )
    ids = [row[0] for row in cr.fetchall()]
    util.recompute_fields(cr, "helpdesk.ticket", ["total_hours_spent"], ids=ids)
