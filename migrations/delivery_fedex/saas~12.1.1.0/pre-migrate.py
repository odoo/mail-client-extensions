# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'delivery_carrier', 'fedex_document_stock_type', 'varchar')
    
    cr.execute("UPDATE delivery_carrier SET fedex_document_stock_type='PAPER_LETTER'")
