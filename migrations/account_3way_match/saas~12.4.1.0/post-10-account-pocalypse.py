# -*- coding: utf-8 -*-


def migrate(cr, version):
    # Update account_move from existing account_invoice.
    cr.execute('''
        UPDATE account_move am
        SET release_to_pay = inv.release_to_pay,
            release_to_pay_manual = inv.release_to_pay_manual,
            force_release_to_pay = inv.force_release_to_pay
        FROM account_invoice inv
        WHERE move_id IS NOT NULL AND am.id = inv.move_id
    ''')
