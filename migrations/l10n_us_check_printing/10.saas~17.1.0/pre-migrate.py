# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        UPDATE res_company
           SET us_check_layout = replace(us_check_layout, '.', '.action_')
    """)
