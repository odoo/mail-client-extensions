# -*- coding: utf-8 -*-

def migrate(cr, version):
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
