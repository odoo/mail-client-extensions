# -*- coding: utf-8 -*-


def migrate(cr, version):
    return
    cr.execute('''
        UPDATE account_move am
           SET document_request_line_id = inv.document_request_line_id
          FROM account_invoice inv
         WHERE inv.move_id = am.id
    ''')
