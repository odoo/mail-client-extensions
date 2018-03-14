# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'stock_move', 'landed_cost_value', 'numeric')
    
    # As in stock_account, the value on the move we set, included the landed cost, as it took the values on the upgraded quants,
    # we need to subtract the applied landed costs from the IN value (as it is not supposed to have them) 
    cr.execute("""
        UPDATE stock_move m SET landed_cost_value = addcost.value, value = m.value - addcost.value
        FROM (SELECT SUM(sval.additional_landed_cost * q.quantity / m_orig.product_qty) AS value, m_all.id AS move_id
                FROM stock_quant q, stock_move m_orig, stock_quant_move_rel sqmr1, stock_quant_move_rel sqmr2, 
                    stock_move m_all, stock_valuation_adjustment_lines sval, stock_location l1, stock_location l2
                WHERE sval.move_id = m_orig.id AND sqmr1.move_id = m_orig.id AND sqmr1.quant_id = q.id 
                    AND sqmr2.quant_id = q.id AND sqmr2.move_id = m_all.id AND q.quantity > 0
                    AND m_all.location_id = l1.id AND m_all.location_dest_id = l2.id
                    AND l1.usage != 'internal' AND (l1.usage != 'transit' OR l1.company_id IS NULL) AND (l2.usage = 'internal' OR (l2.usage = 'transit' AND l2.company_id IS NOT NULL)) 
                GROUP BY m_all.id) addcost
        WHERE m.id = addcost.move_id
    """)
    
    #Upgrade landed costs on OUT moves and subtract (value becomes less negative)
    cr.execute("""
        UPDATE stock_move m SET landed_cost_value = - addcost.value, value = m.value + addcost.value
        FROM (SELECT SUM(sval.additional_landed_cost * q.quantity / m_orig.product_qty) AS value, m_all.id AS move_id
                FROM stock_quant q, stock_move m_orig, stock_quant_move_rel sqmr1, stock_quant_move_rel sqmr2, 
                    stock_move m_all, stock_valuation_adjustment_lines sval, stock_location l1, stock_location l2
                WHERE sval.move_id = m_orig.id AND sqmr1.move_id = m_orig.id AND sqmr1.quant_id = q.id 
                    AND sqmr2.quant_id = q.id AND sqmr2.move_id = m_all.id AND q.quantity > 0
                    AND m_all.location_id = l1.id AND m_all.location_dest_id = l2.id
                    AND (l1.usage = 'internal' or (l1.usage='transit' AND l1.company_id IS NOT NULL)) and l2.usage != 'internal' and (l2.usage != 'transit' OR l2.company_id IS NULL)
                GROUP BY m_all.id) addcost
        WHERE m.id = addcost.move_id
    """)