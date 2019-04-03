# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def update_lang_code(cr, from_, to):
    cr.execute("ALTER TABLE ir_translation DROP CONSTRAINT ir_translation_lang_fkey_res_lang")
    cr.execute("UPDATE ir_translation SET lang = %s WHERE lang = %s", [to, from_])
    cr.execute("UPDATE res_lang SET code = %s WHERE code = %s", [to, from_])
    cr.execute("UPDATE res_partner SET lang = %s WHERE lang = %s", [to, from_])
    if util.column_exists(cr, "payment_transaction", "partner_lang"):
        cr.execute("UPDATE payment_transaction SET partner_lang = %s WHERE partner_lang = %s", [to, from_])
    cr.execute("""
        ALTER TABLE ir_translation
     ADD CONSTRAINT ir_translation_lang_fkey_res_lang
        FOREIGN KEY (lang)
         REFERENCES res_lang(code)
    """)

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

    update_lang_code(cr, "km_KM", "km_KH")
