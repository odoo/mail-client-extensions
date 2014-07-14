# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'product_template', 'track_incoming', 'boolean')
    util.create_column(cr, 'product_template', 'track_outgoing', 'boolean')
    cr.execute("""
        UPDATE product_template SET track_incoming = pp.track_incoming, track_outgoing = pp.track_outgoing
        FROM product_product pp WHERE product_template.id = pp.product_tmpl_id 
    """)
    
    cr.execute("""
        UPDATE stock_move SET priority = '2' 
        WHERE priority = '1'
    """)