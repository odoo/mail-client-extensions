# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("UPDATE res_lang SET iso_code='en' WHERE code='en_US'")
    cr.execute("""
        WITH lang_table AS (
            SELECT id, 'lang_' || COALESCE(iso_code,substring(LOWER(code),'^([a-z]{2})_\\1$')) AS langcode
              FROM res_lang
        )
        INSERT INTO ir_model_data(module, name, model, res_id, noupdate)
           SELECT 'base', langcode, 'res.lang', id, false
             FROM lang_table
            WHERE NOT EXISTS(SELECT 1
                               FROM ir_model_data
                              WHERE module='base'
                                AND name=langcode
                            )
              AND langcode IS NOT NULL
    """)
