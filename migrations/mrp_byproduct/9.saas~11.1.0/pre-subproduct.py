# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'stock_move', 'subproduct_id', 'int4')
    cr.execute("""
        UPDATE stock_move m
           SET subproduct_id = (SELECT max(s.id)
                                  FROM mrp_subproduct s
                                 WHERE s.product_id = m.product_id
                                   AND s.bom_id = p.bom_id)
          FROM mrp_production p
         WHERE p.id = m.production_id
    """)
