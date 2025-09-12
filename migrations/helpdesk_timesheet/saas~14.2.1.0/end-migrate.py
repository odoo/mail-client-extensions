from odoo.upgrade import util


def migrate(cr, version):
    query = """
        SELECT ticket.id
          FROM helpdesk_ticket ticket
          JOIN helpdesk_team team ON ticket.team_id = team.id
         WHERE team.use_helpdesk_timesheet IS TRUE
        """
    util.recompute_fields(cr, "helpdesk.ticket", ["total_hours_spent"], query=query)
