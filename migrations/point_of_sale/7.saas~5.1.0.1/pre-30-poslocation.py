# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'pos_config', 'stock_location_id', 'int4')
    util.create_column(cr, 'pos_config', 'company_id', 'int4')
    cr.execute("""UPDATE pos_config
                     SET stock_location_id = sw.lot_stock_id.
                         company_id = sw.company_id
                    FROM stock_warehouse sw
                   WHERE sw.id = pos_config.warehouse_id
    """)
