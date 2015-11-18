# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    """
        Fiscal Year object does not exists anymore, instead we have lock date on company.
        Thus we need to write those lock date based on current FY
    """

    util.create_column(cr, 'res_company', 'fiscalyear_last_day', 'int4')
    util.create_column(cr, 'res_company', 'fiscalyear_last_month', 'int4')
    util.create_column(cr, 'res_company', 'period_lock_date', 'date')
    util.create_column(cr, 'res_company', 'fiscalyear_lock_date', 'date')

    cr.execute("""UPDATE res_company c 
                    SET fiscalyear_last_day = fy.fy_last_day, 
                        fiscalyear_last_month = fy.fy_last_month,
                        fiscalyear_lock_date = fy.fy_lock_date,
                        period_lock_date = fy.p_lock_date
                    FROM (SELECT date_part('day', max(f.date_stop)) AS fy_last_day,
                        f.company_id,
                        date_part('month', max(f.date_stop)) AS fy_last_month,
                        max(p.date_stop) AS p_lock_date,
                        max(f.date_stop) AS fy_lock_date
                        FROM account_fiscalyear f 
                        LEFT JOIN account_period p ON p.state = 'done' 
                        WHERE f.state = 'done' GROUP BY f.company_id) fy
                    WHERE fy.company_id = c.id
                """)
    #It is possible that some company did not have any close FY meaning that recquires field 
    # fiscalyear_last_day/month has not been setted by previous request and need to be set using
    # default value
    cr.execute("""UPDATE res_company
                    SET fiscalyear_last_day = 31,
                        fiscalyear_last_month = 12
                    WHERE fiscalyear_last_day IS NULL AND fiscalyear_last_month IS NULL
                """)