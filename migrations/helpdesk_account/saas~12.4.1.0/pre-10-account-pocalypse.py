# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute('ALTER TABLE account_invoice_helpdesk_ticket_rel RENAME TO account_invoice_helpdesk_ticket_rel_old')
