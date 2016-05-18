# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        UPDATE account_move m
           SET asset_id = l.asset_id
          FROM account_move_line l
         WHERE m.id = l.move_id
           AND l.asset_id IS NOT NULL
    """)
