# -*- coding: utf-8 -*-

def migrate(cr, version):
    # force update all templates
    cr.execute("""
        UPDATE ir_model_data d
           SET noupdate=false
          FROM ir_ui_view v
         WHERE d.model = 'ir.ui.view'
           AND d.res_id = v.id
           AND d.module = 'website_sale'
           AND v.type = 'qweb'
    """)
