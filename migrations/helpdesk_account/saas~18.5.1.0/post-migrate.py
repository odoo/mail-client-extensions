from odoo.upgrade import util


def migrate(cr, version):
    query = """
        WITH ticket_cte AS (
            SELECT a.id,
                   MIN(rel.helpdesk_ticket_id) AS helpdesk_ticket_id
              FROM account_move a
              JOIN account_move_helpdesk_ticket_rel rel
                ON rel.account_move_id = a.id
             WHERE {parallel_filter}
             GROUP BY a.id
        )
        UPDATE account_move a
           SET ticket_id = ticket_cte.helpdesk_ticket_id
          FROM ticket_cte
         WHERE a.id = ticket_cte.id
    """
    util.explode_execute(cr, query, table="account_move", alias="a")
