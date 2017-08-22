# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    """
        The concept of period does not exist anymore, instead write last period date on date field on model
    """

    #Do the same for account_move
    cr.execute("""UPDATE account_move a
                    SET date = p.date_stop
                    FROM account_period p
                    WHERE p.id = a.period_id AND ((a.date NOT BETWEEN p.date_start AND p.date_stop) OR a.date IS NULL)
                """)

    #Set the related date on account_move_line
    cr.execute("""UPDATE account_move_line aml 
                    SET date = am.date 
                    FROM account_move am 
                    WHERE aml.move_id = am.id
                """)

    #and again on account_bank_statement
    cr.execute("""UPDATE account_bank_statement a
                    SET date = p.date_stop
                    FROM account_period p
                    WHERE p.id = a.period_id AND ((a.date NOT BETWEEN p.date_start AND p.date_stop) OR a.date IS NULL)
                """)

    util.create_column(cr, 'account_invoice', 'date', 'date')

    #and again on account_invoice
    cr.execute("""UPDATE account_invoice a
                    SET date = p.date_stop
                    FROM account_period p
                    WHERE p.id = a.period_id AND ((a.date_invoice NOT BETWEEN p.date_start AND p.date_stop) OR a.date_invoice IS NULL)
                """)

    #Set the date on account_invoice related 'date_invoice' is not null
    cr.execute("""UPDATE account_invoice
                    SET date = date_invoice
                    WHERE date_invoice is not null AND date is null AND state not in ('draft','cancel');
                """)
