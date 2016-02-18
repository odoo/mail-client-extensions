# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'ir_model_fields', 'store', 'boolean')
    cr.execute("""
        UPDATE ir_model_fields
           SET store=(compute IS NULL AND related IS NULL)
         WHERE state='manual'
    """)

    util.force_noupdate(cr, 'base.view_model_form', False)
    util.force_noupdate(cr, 'base.view_model_fields_form', False)
