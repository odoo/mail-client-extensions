from odoo.upgrade import util


def migrate(cr, version):
    query = """
        SELECT ticket.id
          FROM helpdesk_ticket ticket
          JOIN helpdesk_team team ON ticket.team_id = team.id
         WHERE team.use_helpdesk_sale_timesheet IS TRUE
        """
    util.recompute_fields(cr, "helpdesk.ticket", ["sale_line_id", "sale_order_id"], query=query)
