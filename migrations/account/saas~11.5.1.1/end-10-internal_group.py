# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("""
        UPDATE account_account a
           SET internal_group = t.internal_group
          FROM account_account_type t
         WHERE t.id = a.user_type_id
    """)
