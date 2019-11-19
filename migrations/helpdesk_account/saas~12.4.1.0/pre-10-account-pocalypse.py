# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute('ALTER TABLE account_invoice_helpdesk_ticket_rel RENAME TO account_invoice_helpdesk_ticket_rel_old')
    util.create_m2m(cr, "account_move_helpdesk_ticket_rel", "helpdesk_ticket", "account_move")
