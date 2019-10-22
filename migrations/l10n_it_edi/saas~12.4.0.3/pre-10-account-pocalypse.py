# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, 'account_move', 'l10n_it_send_state', 'varchar')
    util.create_column(cr, 'account_move', 'l10n_it_stamp_duty', 'float8')
    util.create_column(cr, 'account_move', 'l10n_it_ddt_id', 'int4')
    util.create_column(cr, 'account_move', 'l10n_it_einvoice_name', 'varchar')
    util.create_column(cr, 'account_move', 'l10n_it_einvoice_id', 'int4')

    # Migrate values from account_invoice to account_move.
    cr.execute('''
        UPDATE account_move am
        SET l10n_it_send_state = inv.l10n_it_send_state,
            l10n_it_stamp_duty = inv.l10n_it_stamp_duty,
            l10n_it_ddt_id = inv.l10n_it_ddt_id,
            l10n_it_einvoice_name = inv.l10n_it_einvoice_name,
            l10n_it_einvoice_id = inv.l10n_it_einvoice_id
        FROM account_invoice inv
        WHERE move_id IS NOT NULL AND am.id = inv.move_id
    ''')
