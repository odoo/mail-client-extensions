# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'ir_attachment', 'product_downloadable', 'boolean')
    cr.execute("""
        UPDATE ir_attachment
           SET type='service', product_downloadable=true
         WHERE type='digital'
    """)
