# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, 'account_move', 'l10n_ch_isr_number', 'varchar')

    cr.execute('''
        UPDATE account_move am
        SET l10n_ch_isr_number = inv.l10n_ch_isr_number
        FROM account_invoice inv
        WHERE move_id IS NOT NULL AND am.id = inv.move_id
    ''')
