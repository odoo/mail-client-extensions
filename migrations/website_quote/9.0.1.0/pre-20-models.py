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
        cr.execute("UPDATE sale_quote_template SET require_payment=NULL WHERE require_payment=0")
    if util.column_exists(cr, 'sale_order', 'require_payment'):
        cr.execute("""
            ALTER TABLE sale_order
           ALTER COLUMN require_payment
          SET DATA TYPE int
                  USING require_payment::int
        """)
        cr.execute("UPDATE sale_order SET require_payment=NULL WHERE require_payment=0")
