# -*- coding: utf-8 -*-

def migrate(cr, version):
    """
    Adapt sale order workflow to be entirely in sale module instead of sale_stock
    """
    cr.execute("""UPDATE ir_model_data
                     SET module = %s
                   WHERE module = %s
                     AND model IN %s
               """, ('sale', 'sale_stock', ('workflow.activity', 'workflow.transition')))
