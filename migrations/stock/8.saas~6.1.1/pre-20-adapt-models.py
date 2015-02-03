# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # store and pre-compute related fields
    util.create_column(cr, 'stock_picking', 'location_id', 'int4')
    util.create_column(cr, 'stock_picking', 'location_dest_id', 'int4')

    cr.execute("""
        WITH locs AS (
            SELECT p.id,
                   (array_agg(m.location_id order by m.date_expected desc, m.id))[1] as loc_id,
                   (array_agg(m.location_dest_id order by m.date_expected desc, m.id))[1] as loc_dest_id
              FROM stock_picking p
         LEFT JOIN stock_move m
                ON m.picking_id = p.id
          GROUP BY p.id
        )
        UPDATE stock_picking p
           SET location_id = l.loc_id,
               location_dest_id = l.loc_dest_id
          FROM locs l
         WHERE l.id = p.id
    """)
