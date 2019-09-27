# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute('''
        UPDATE account_move am
        SET website_id = inv.website_id
        FROM account_invoice inv
        WHERE inv.move_id = am.id
    ''')
