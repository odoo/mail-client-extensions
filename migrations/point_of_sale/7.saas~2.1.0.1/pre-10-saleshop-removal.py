# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
def migrate(cr, version):
    """
        sale.shop model does not exists anymore.
    """
    util.create_column(cr, 'pos_config', 'warehouse_id', 'int4')
    util.create_column(cr, 'pos_config', 'pricelist_id', 'int4')

    cr.execute("""
        UPDATE pos_config c
           SET warehouse_id = s.warehouse_id,
               pricelist_id = s.pricelist_id
          FROM sale_shop s
         WHERE s.id = c.shop_id
    """)
