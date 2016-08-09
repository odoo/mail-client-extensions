# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'stock_move', 'scrapped', 'boolean')
    cr.execute("""
        UPDATE stock_move m
           SET scrapped = l.scrap_location
          FROM stock_location l
         WHERE l.id = m.location_dest_id
    """)

    util.create_column(cr, 'stock_production_lot', 'product_uom_id', 'int4')
    cr.execute("""
        UPDATE stock_production_lot l
           SET product_uom_id = t.uom_id
          FROM product_product p, product_template t
         WHERE p.id = l.product_id
           AND t.id = p.product_tmpl_id
    """)
