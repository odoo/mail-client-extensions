# -*- coding: utf-8 -*-

def migrate(cr, version):
    # remove empty and duplicated translation (allow creation of unique index)
    cr.execute("DELETE FROM ir_translation WHERE trim(coalesce(value, '')) = ''")
    cr.execute("""
        DELETE FROM ir_translation WHERE id IN (
             SELECT unnest((array_agg(id ORDER BY id))[2:array_length(array_agg(id), 1)])
               FROM ir_translation
           GROUP BY type, name, lang, res_id, src
             HAVING count(id) > 1
        )
    """)

    cr.execute("UPDATE res_lang SET code='km_KH' WHERE code='km_KM'")
