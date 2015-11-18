# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    """
        We delete account voucher that has a type different than sale/purchase as it does not exists anymore in v9
    """
    cr.execute("""DELETE FROM account_voucher
                   WHERE type NOT IN ('sale', 'purchase')
               """)

    """
        The concept of period does not exist anymore, instead write last period date on date field on model
    """

    #On account voucher, if the date field is already between the period date let it as be, otherwise
    #set the date as the date_stop from the period
    cr.execute("""UPDATE account_voucher a
                    SET date = p.date_stop
                    FROM account_period p
                    WHERE p.id = a.period_id AND ((a.date NOT BETWEEN p.date_start AND p.date_stop) OR a.date IS NULL)
                """)