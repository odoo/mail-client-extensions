# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Match inventory lines
    cr.execute("""SELECT il.inventory_id, il.product_id, il.theoretical_qty, il.product_qty, il.product_uom_id, 
                            il.prod_lot_id, il.partner_id, il.package_id
                    FROM stock_inventory_line il, stock_inventory i 
                    WHERE il.inventory_id = i.id AND i.state = 'done'
    """)
    res = cr.fetchall()
    for re in res:
        package = None
        result_package = None
        # location query (not possible when theoretical_qty is not defined)
        product_qty = 0
        location_query = " "
        if re[2]:
            if re[2] > re[3]: # out case (theoretical qty > product qty)
                location_query = " AND l1.usage != 'inventory' AND l2.usage = 'inventory'" #inventory is virtual location, not internal
                product_qty = re[2] - re[3]
                if re[7]:
                    package = re[7]
            elif re[2] < re[3]: # in case
                location_query = " AND l1.usage = 'inventory' AND l2.usage != 'inventory'"
                product_qty = re[3] - re[2]
                if re[7]:
                    result_package = re[7]
            else:
                continue
        query = """
            INSERT INTO stock_move_line
            (move_id, product_id, product_uom_id, product_qty, product_uom_qty, qty_done, lot_id, owner_id, package_id, result_package_id, state,
             location_id, location_dest_id, date, reference)
            SELECT m.id, m.product_id, m.product_uom, 0.0, 0.0, m.product_qty, m.restrict_lot_id, m.restrict_partner_id, %s, %s, 'done', 
                    m.location_id, m.location_dest_id, m.date, m.name
                FROM stock_move m, stock_location l1, stock_location l2
                WHERE l1.id = m.location_id AND l2.id = m.location_dest_id
                    AND m.inventory_id = %s AND m.product_id = %s AND m.product_uom = %s
                    AND NOT EXISTS (SELECT id FROM stock_move_line sl WHERE sl.move_id = m.id) 
        """

        params = (package, result_package, re[0], re[1], re[4],)
        # It is possible the theoretical_qty was not defined in e.g. v7
        if product_qty:
            query += " AND product_uom_qty = %s "
            params += (product_qty,)
        if re[5]:
            query += " AND restrict_lot_id = %s "
            params += (re[5],)
        else:
            query += " AND restrict_lot_id IS NULL "
        if re[6]:
            query += " AND restrict_partner_id = %s "
            params += (re[6],)
        else:
            query += " AND restrict_partner_id IS NULL "
        query += location_query
        query += """ LIMIT 1"""
        cr.execute(query, params)

