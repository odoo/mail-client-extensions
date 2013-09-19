# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
def migrate(cr, version):
    """
        sale.shop model does not exists anymore.
    """
    util.create_column(cr, 'sale_order', 'warehouse_id', 'int4')

    cr.execute("""
        UPDATE sale_order o
           SET warehouse_id = s.warehouse_id
          FROM sale_shop s
         WHERE s.id = o.shop_id
    """)
