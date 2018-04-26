# -*- coding: utf-8 -*-

def migrate(cr, version):
    # Since odoo/odoo@8f88c0336f881dd59d7c25b64c5bcba1989f998b, search views' filters MUST have
    # a `name`. Force update
    cr.execute("""
        UPDATE ir_model_data
           SET noupdate = false
         WHERE noupdate = true
           AND model = 'ir.ui.view'
           AND COALESCE(module, '') NOT IN ('', '__export__')
           AND res_id IN (SELECT id FROM ir_ui_view WHERE type='search')
    """)
