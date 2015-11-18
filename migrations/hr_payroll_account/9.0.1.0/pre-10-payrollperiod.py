# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    """
        The concept of period does not exist anymore, instead write last period date on date field on model
    """

    #date fields should not exist yet since it has been added in v9
    util.create_column(cr, 'hr_payslip', 'date', 'date')

    cr.execute("""UPDATE hr_payslip hr
                    SET date = p.date_stop
                    FROM account_period p
                    WHERE p.id = hr.period_id
                """)