# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.table_exists(cr, "ir_translation"):
        return

    cr.execute(
        """
        DELETE FROM ir_translation
         WHERE lang IS NULL
            OR COALESCE(value, '') = ''
            OR (value = src AND type IS DISTINCT FROM 'model')
        """
    )
