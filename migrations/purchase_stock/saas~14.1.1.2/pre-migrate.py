# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "stock_warehouse_orderpoint", "vendor_id", "int4")
    cr.execute(
        """
            UPDATE stock_warehouse_orderpoint o
               SET vendor_id = s.name
              FROM product_supplierinfo s
             WHERE s.id = o.supplier_id
        """
    )
