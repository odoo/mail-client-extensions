# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        UPDATE ir_model_data
           SET noupdate = false
         WHERE model = 'ir.ui.view'
           AND COALESCE(module, '') NOT IN ('', '__export__')
           AND name IN ('assets_common', 'assets_backend', 'assets_frontend', 'assets_editor')
    """)
