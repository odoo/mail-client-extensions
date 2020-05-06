# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):

    # ===========================================================
    # Currency on all account.move.line (PR:50711 & 10394)
    # ===========================================================

    util.remove_field(cr, 'account.move.line', 'always_set_currency_id')

    cr.execute('''
        ALTER TABLE account_move_line
        DROP CONSTRAINT account_move_line_check_amount_currency_balance_sign
    ''')

    cr.execute('''
        UPDATE account_move_line
        SET 
            currency_id = company_currency_id,
            amount_currency = balance
        WHERE currency_id IS NULL
    ''')

    # Prevent inconsistencies in others scripts by adding the updated constraint manually.
    cr.execute('''
        ALTER TABLE account_move_line 
        ADD CONSTRAINT account_move_line_check_amount_currency_balance_sign 
        CHECK(
            (
                (currency_id != company_currency_id)
                AND
                (
                    (debit - credit <= 0 AND amount_currency <= 0)
                    OR
                    (debit - credit >= 0 AND amount_currency >= 0)
                )
            )
            OR
            (
                currency_id = company_currency_id
                AND
                ROUND(debit - credit - amount_currency, 2) = 0
            )
        )
    ''')
