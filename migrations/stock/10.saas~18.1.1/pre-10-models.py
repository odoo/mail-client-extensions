# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'product_template', 'responsible_id', 'int4')
    cr.execute("UPDATE product_template SET responsible_id = COALESCE(create_uid, %s)",
               [SUPERUSER_ID])

    util.remove_field(cr, 'product_template', 'property_stock_procurement')

    util.create_column(cr, 'stock_move', 'reference', 'varchar')
    cr.execute("""
      WITH refs AS (
            SELECT m.id as id, COALESCE(p.name, m.name) as name
              FROM stock_move m
         LEFT JOIN stock_picking p ON (p.id = m.picking_id)
      )
        UPDATE stock_move m
           SET "reference" = refs.name
          FROM refs
         WHERE refs.id = m.id
    """)

    util.remove_model(cr, 'procurement.orderpoint.compute')
