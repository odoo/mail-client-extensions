# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # it's not a function field but it should probably have been
    util.create_column(cr, 'sale_order_line', 'qty_delivered', 'float8')
    cr.execute("""
        UPDATE sale_order_line SET
            qty_delivered = query.sum
            FROM (
                SELECT sol.id, sum(mv.product_qty)
                FROM stock_move AS mv,
                     stock_location AS loc,
                     procurement_order AS proc,
                     sale_order_line AS sol
                WHERE mv.location_dest_id=loc.id AND
                      mv.state='done' AND
                      loc.usage='customer' AND
                      loc.scrap_location='f' AND
                      mv.procurement_id=proc.id AND
                      proc.sale_line_id=sol.id
                GROUP BY sol.id) AS query
            WHERE query.id = sale_order_line.id;
        """)