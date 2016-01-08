# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("UPDATE res_lang SET iso_code='en' WHERE code='en_US'")
    cr.execute("""
        INSERT INTO ir_model_data(module, name, model, res_id, noupdate)
           SELECT 'base', 'lang_' || iso_code, 'res.lang', id, false
             FROM res_lang l
            WHERE NOT EXISTS(SELECT 1
                               FROM ir_model_data
                              WHERE module='base'
                                AND name='lang_' || l.iso_code)
    """)
