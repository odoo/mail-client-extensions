# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("""
        UPDATE account_move_line l
           SET l10n_pe_group_id = a.group_id
          FROM account_account a
         WHERE a.id = l.account_id
    """)
