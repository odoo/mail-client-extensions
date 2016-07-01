# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("UPDATE account_payment_term_line SET value = 'percent' WHERE value = 'procent'")

    util.create_column(cr, 'account_payment_term_line', 'option', 'varchar')
    cr.execute("""
        UPDATE account_payment_term_line
           SET days = CASE WHEN days2 > 0 THEN COALESCE(days, 0) + days2
                           ELSE days
                       END,
               option = CASE WHEN COALESCE(days2, 0) = 0 THEN 'day_after_invoice_date'
                             ELSE 'fix_day_following_month'
                         END
    """)
