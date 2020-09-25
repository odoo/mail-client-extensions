# -*- coding: utf-8 -*-


def migrate(cr, version):
    # Reset the company of partner if there is a statement line belonging to another company
    cr.execute(
        """
            UPDATE res_partner p
               SET company_id = NULL
              FROM account_bank_statement_line l
              JOIN account_journal j ON j.id = l.journal_id
             WHERE l.partner_id = p.id
               AND p.company_id IS NOT NULL
               AND j.company_id != p.company_id
        """
    )
