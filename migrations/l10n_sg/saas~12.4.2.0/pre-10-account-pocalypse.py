# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, 'account_move', 'l10n_sg_permit_number', 'varchar')
    util.create_column(cr, 'account_move', 'l10n_sg_permit_number_date', 'date')

    # Migrate values from account_invoice to account_move.
    cr.execute('''
        UPDATE account_move am
        SET l10n_sg_permit_number = inv.l10n_sg_permit_number,
            l10n_sg_permit_number_date = inv.l10n_sg_permit_number_date
        FROM account_invoice inv
        WHERE move_id IS NOT NULL AND am.id = inv.move_id
    ''')
