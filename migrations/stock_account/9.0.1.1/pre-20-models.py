# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_field(cr, 'product_template', 'valuation', 'property_valuation')
    util.rename_field(cr, 'product_template', 'cost_method', 'property_cost_method')

    for prop in ['input', 'output']:
        util.rename_field(cr, 'product.category',
                        'property_stock_account_%s_categ' % prop,
                        'property_stock_account_%s_categ_id' % prop)

    util.create_column(cr, 'stock_inventory', 'accounting_date', 'timestamp without time zone')
    cr.execute("""
        UPDATE stock_inventory i
           SET accounting_date = p.date_stop
          FROM account_period p
         WHERE p.id = i.period_id
           AND i.date NOT BETWEEN p.date_start AND p.date_stop
    """)
