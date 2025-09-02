# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.table_exists(cr, "_ir_translation"):
        cr.execute("ALTER TABLE _ir_translation DROP CONSTRAINT IF EXISTS ir_translation_lang_fkey_res_lang")

    if util.table_exists(cr, "ir_translation"):
        cr.execute(
            """
            DELETE FROM ir_translation
             WHERE lang IS NULL
                OR COALESCE(value, '') = ''
                OR (value = src AND type IS DISTINCT FROM 'model')
                OR (src IS NULL AND type = 'model_terms')
            """
        )
