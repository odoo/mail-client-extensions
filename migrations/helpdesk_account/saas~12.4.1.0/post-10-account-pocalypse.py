# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_m2m('account_move_helpdesk_ticket_rel', 'helpdesk_ticket_id', 'account_move_id')

    cr.execute('''
        UPDATE account_move_helpdesk_ticket_rel
        SET account_move_id = inv.move_id
        FROM account_invoice_helpdesk_ticket_rel_old rel
        JOIN account_invoice inv ON inv.id = rel.account_invoice_id;
        
        DROP TABLE account_invoice_helpdesk_ticket_rel_old CASCADE;
    ''')
