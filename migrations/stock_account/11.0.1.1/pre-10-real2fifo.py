# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # Columns needed on stock_move to support FIFO
    util.create_column(cr, 'stock_move', 'value', 'numeric')
    util.create_column(cr, 'stock_move', 'remaining_value', 'numeric')
    util.create_column(cr, 'stock_move', 'remaining_qty', 'numeric')
    
    
    # In order to support FIFO instead of real price,  
    # we initiate the stock move's new FIFO values with the real price values.  
    # So the remaining qty/remaining_value will be initiated with the sum of the quants of that incoming move that are still in stock
    # according to the real price.  This way the value of the stock does not need to change during migration
    # We just need to make sure we add the 

    # Positive remaining_qty, remaining_value
    cr.execute("""
        UPDATE stock_move m SET remaining_qty = upl.remaining_qty, remaining_value = upl.remaining_value
        FROM (SELECT m2.id AS id, SUM(q.quantity) AS remaining_qty, SUM(q.cost * q.quantity) AS remaining_value
                FROM stock_quant_move_rel sqmr, stock_quant q, stock_location l, stock_move m2
                WHERE sqmr.move_id = m2.id AND q.id = sqmr.quant_id
                AND l.id = q.location_id AND l.usage IN ('internal', 'transit') AND l.company_id IS NOT NULL AND q.quantity > 0
                AND NOT EXISTS(SELECT m3.id FROM stock_move m3, stock_quant_move_rel r2, stock_location l11, stock_location l12
                                WHERE r2.quant_id = q.id AND m3.id = r2.move_id AND m3.id != m2.id 
                                    AND ((m3.date > m2.date) OR (m3.date = m2.date and m3.id > m2.id)) 
                                    AND m3.location_id = l11.id AND m3.location_dest_id = l12.id
                                    AND l11.usage != 'internal' AND (l11.usage != 'transit' OR l11.company_id IS NULL) 
                                    AND (l12.usage = 'internal' OR (l12.usage = 'transit' AND l12.company_id IS NOT NULL))
                                    )
                GROUP BY m2.id) upl, 
            stock_location l1, stock_location l2 
        WHERE l1.usage != 'internal' AND (l1.usage != 'transit' OR l1.company_id IS NULL) AND (l2.usage = 'internal' OR (l2.usage = 'transit' AND l2.company_id IS NOT NULL))
            AND m.location_id = l1.id AND m.location_dest_id = l2.id
            AND upl.id = m.id
    """)
    
    # Negative remaining_qty for outs that generated negative quants
    # Remaining_value should be 0 as they were not written for the out
    cr.execute("""
        UPDATE stock_move m SET remaining_qty = upl.remaining_qty, remaining_value = upl.remaining_value
        FROM (SELECT m2.id AS id, - SUM(q.quantity) AS remaining_qty, 0.0 AS remaining_value
                FROM stock_quant_move_rel sqmr, stock_quant q, stock_move m2
                WHERE sqmr.move_id = m2.id AND q.id = sqmr.quant_id
                 AND q.quantity > 0 AND q.propagated_from_id IS NOT NULL
                 AND NOT EXISTS (SELECT m3.id FROM stock_move m3, stock_quant_move_rel r2, stock_location l11, stock_location l12
                                WHERE r2.quant_id = q.id AND m3.id = r2.move_id AND m3.id != m2.id 
                                    AND ((m3.date > m2.date) OR (m3.date = m2.date and m3.id > m2.id)) 
                                    AND m3.location_id = l11.id AND m3.location_dest_id = l12.id
                                    AND l12.usage != 'internal' AND (l12.usage != 'transit' OR l12.company_id IS NULL) 
                                    AND (l11.usage = 'internal' OR (l11.usage = 'transit' AND l11.company_id IS NOT NULL))
                                    )
                GROUP BY m2.id) upl, 
            stock_location l1, stock_location l2 
        WHERE (l1.usage = 'internal' or (l1.usage='transit' AND l1.company_id IS NOT NULL)) and l2.usage != 'internal' and (l2.usage != 'transit' OR l2.company_id IS NULL)
            AND m.location_id = l1.id AND m.location_dest_id = l2.id
            AND upl.id = m.id
    """)
    
    # Real cost method was replaced by FIFO cost method (LIFO not implemented yet)
    cr.execute("""
        UPDATE ir_property SET value_text='fifo' 
            WHERE value_text='real' and fields_id in (SELECT id FROM ir_model_fields WHERE name='property_cost_method')
    """)
    cr.execute(
        """
        UPDATE ir_default
           SET json_value='"fifo"'
         WHERE json_value='"real"'
           AND field_id in (SELECT id FROM ir_model_fields WHERE name in ('property_cost_method','cost_method'))
        """
    )

    #price_unit and value positive in case of in
    cr.execute("""UPDATE stock_move m SET price_unit = qupi.price, value = qupi.value
                        FROM (SELECT m2.id AS move_id, SUM(q.quantity * q.cost) / m2.product_qty AS price, SUM(q.quantity * q.cost) AS value
                                FROM stock_move m2, stock_quant_move_rel sqmr, stock_quant q, stock_location l1, stock_location l2 
                                WHERE sqmr.move_id = m2.id AND sqmr.quant_id = q.id AND q.quantity > 0 AND m2.product_qty > 0
                                    AND l1.id = m2.location_id AND l2.id = m2.location_dest_id
                                    AND l1.usage != 'internal' AND (l1.usage != 'transit' OR l1.company_id IS NULL) AND (l2.usage = 'internal' OR (l2.usage = 'transit' AND l2.company_id IS NOT NULL))
                                GROUP BY m2.id) qupi 
                        WHERE qupi.move_id = m.id""")
    
    # price_unit and value negative in out case
    # Value will be corrected by fixed fifo_vacuum afterwards
    cr.execute("""UPDATE stock_move m SET price_unit = qupi.price, value = qupi.value
                        FROM (SELECT m2.id AS move_id, - SUM(q.quantity * q.cost) / m2.product_qty AS price, -SUM(q.quantity * q.cost) AS value
                                FROM stock_move m2, stock_quant_move_rel sqmr, stock_quant q, stock_location l1, stock_location l2 
                                WHERE sqmr.move_id = m2.id AND sqmr.quant_id = q.id AND q.quantity > 0 AND m2.product_qty > 0
                                    AND q.propagated_from_id IS NULL
                                    AND l1.id = m2.location_id AND l2.id = m2.location_dest_id
                                    AND (l1.usage = 'internal' or (l1.usage='transit' AND l1.company_id IS NOT NULL)) and l2.usage != 'internal' and (l2.usage != 'transit' OR l2.company_id IS NULL)
                                GROUP BY m2.id) qupi 
                        WHERE qupi.move_id = m.id""")
    

    #create index to speedup the matching below
    cr.execute("""create index account_move_line_name_mig_only on account_move_line using hash (name)""")
    cr.execute("""create index stock_move_name_mig_only on stock_move using hash (name)""")
    cr.execute("""create index stock_picking_mig_only on stock_picking using hash (name)""")
    cr.execute("""create index account_move_name_mig_only on account_move using hash (name)""")
    cr.execute("""create index account_move_line_ref_mig_only on account_move_line using hash (ref)""")
    cr.execute("""create index account_move_ref_mig_only on account_move using hash (ref)""")


    # Create link between account move and stock move (based on reference/name matching)
    util.create_column(cr, 'account_move', 'stock_move_id', 'int4')
    cr.execute("""
        UPDATE account_move am SET stock_move_id = movematch.stock_move_id 
        FROM (SELECT am.id AS account_move_id, m.id AS stock_move_id 
                FROM account_move_line aml, stock_move m, stock_picking p, account_move am
                WHERE aml.move_id = am.id AND m.picking_id = p.id AND aml.name=m.name 
                    AND aml.ref = p.name AND am.ref = p.name 
                GROUP BY am.id, m.id) movematch
        WHERE am.id = movematch.account_move_id
    """)

    # Create link between account move and stock move (based name only where there is no picking_id)
    # Less precise than the previous query, se we do not overwrite previously created matching
    cr.execute("""UPDATE account_move am SET stock_move_id = movematch.stock_move_id FROM 
                    (
                        SELECT am.id AS account_move_id, min(sm.id ) stock_move_id
                        FROM account_move_line aml, stock_move sm, account_move am 
                        WHERE 
                        aml.move_id = am.id AND sm.product_id=aml.product_id
                        AND aml.name=sm.name
                        AND sm.picking_id is null
                        GROUP BY am.id, sm.id
                        HAVING count(distinct(sm.id )) = 1 
                    ) movematch
                    WHERE am.id = movematch.account_move_id
                    AND am.stock_move_id is null""")

    #drop index to speedup the matching
    cr.execute("""drop index account_move_line_name_mig_only """)
    cr.execute("""drop index stock_move_name_mig_only """)
    cr.execute("""drop index stock_picking_mig_only """)
    cr.execute("""drop index account_move_name_mig_only """)
    cr.execute("""drop index account_move_line_ref_mig_only """)
    cr.execute("""drop index account_move_ref_mig_only """)


    # update quantity for account_move_line (only used during inventory valuation with a specified date)
        # The quantity on the account_move_line sould have the same sign as the balance.
        # If the valuation for the line is +10$ make sure the quantity is positive (add money = add quantity)
        # Shortly, quantity should have the same sign as the balance
    cr.execute("""update account_move_line set quantity = abs(quantity)*sign(balance) where quantity is not null and balance <> 0""")
