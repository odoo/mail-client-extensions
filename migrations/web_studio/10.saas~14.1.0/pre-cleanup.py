# -*- coding: utf-8 -*-

def migrate(cr, version):
    # cleanup wrongly created xmlids, see https://git.io/vMX2D
    cr.execute("""
        DELETE FROM ir_model_data
              WHERE module='web_studio'
                AND model='ir.model'
    """)
