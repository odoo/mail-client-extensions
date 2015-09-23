# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if util.column_exists(cr, 'sale_quote_template', 'require_payment'):
        cr.execute("""
            ALTER TABLE sale_quote_template
           ALTER COLUMN require_payment
          SET DATA TYPE int
                  USING require_payment::int
        """)
    if util.column_exists(cr, 'sale_order', 'require_payment'):
        cr.execute("""
            ALTER TABLE sale_order
           ALTER COLUMN require_payment
          SET DATA TYPE int
                  USING require_payment::int
        """)
