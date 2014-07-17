# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if not util.column_exists(cr, 'product_template', 'produce_delay'):
        util.create_column(cr, 'product_template', 'produce_delay', 'float')
        cr.execute("""
            UPDATE product_template SET produce_delay = pp.produce_delay
            FROM product_product pp
            WHERE product_template.id = pp.product_tmpl_id
        """)
    util.create_column(cr, 'product_template', 'track_production', 'boolean')
    cr.execute("""
        UPDATE product_template SET track_production = pp.track_production
        FROM product_product pp WHERE product_template.id = pp.product_tmpl_id 
    """)