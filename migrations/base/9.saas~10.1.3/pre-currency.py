# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        INSERT INTO ir_model_data(module, name, model, res_id, noupdate)
             SELECT 'base', name, 'res.currency', id, true
               FROM res_currency c
              WHERE name IN ('IDR')
                AND NOT EXISTS(SELECT 1
                                 FROM ir_model_data
                                WHERE model='res.currency'
                                  AND name=c.name)
    """)
