# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
   INSERT INTO account_move_helpdesk_ticket_rel (account_move_id, helpdesk_ticket_id)
        SELECT inv.move_id, rel.helpdesk_ticket_id
          FROM account_invoice_helpdesk_ticket_rel_old rel
          JOIN account_invoice inv ON inv.id = rel.account_invoice_id
        """
    )
    cr.execute("DROP TABLE account_invoice_helpdesk_ticket_rel_old CASCADE")
