# -*- coding: utf-8 -*-

def migrate(cr, version):
    # since old-api is gone, all server actions will need to be updated.
    cr.execute("""
        UPDATE ir_model_data
           SET noupdate=false
         WHERE model='ir.actions.server'
           AND module NOT IN ('', '__export__')
    """)
