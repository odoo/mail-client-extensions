# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    """
        account.payment.term.line: value field, rename procent selection into percent + 
            day2 == -1  => set option to 'last_day_current_month'
            day2 == 0 => do nothing
            day2 >0 => set option to 'fix_day_following_month'
    """

    cr.execute("""UPDATE account_payment_term_line
                   SET value = 'percent' WHERE value = 'procent'
               """)

    util.create_column(cr, 'account_payment_term_line', 'option', 'varchar')

    cr.execute("""UPDATE account_payment_term_line
                    SET option = 'last_day_current_month' WHERE days2 = -1
            """)

    cr.execute("""UPDATE account_payment_term_line
                    SET option = 'fix_day_following_month' WHERE days2 > 0
            """)

    cr.execute("""UPDATE account_payment_term_line
                    SET option = 'day_after_invoice_date' WHERE days2 = 0
            """)