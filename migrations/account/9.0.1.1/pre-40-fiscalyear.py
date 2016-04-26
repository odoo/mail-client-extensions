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

    cr.execute("""
        UPDATE res_company c
           SET fiscalyear_last_day = fy.fy_last_day,
               fiscalyear_last_month = fy.fy_last_month
          FROM (SELECT company_id,
                       date_part('day', max(date_stop)) AS fy_last_day,
                       date_part('month', max(date_stop)) AS fy_last_month
                  FROM account_fiscalyear
              GROUP BY company_id) fy
         WHERE fy.company_id = c.id
    """)
    # default values for companies without any fiscalyear set
    cr.execute("""UPDATE res_company
                    SET fiscalyear_last_day = 31,
                        fiscalyear_last_month = 12
                    WHERE fiscalyear_last_day IS NULL AND fiscalyear_last_month IS NULL
                """)

    # lock_dates are max(date_stop of done fy/p) OR min(date_start-1day of draft fy/p)
    for tbl in ('fiscalyear', 'period'):
        cr.execute("""
          UPDATE res_company c
             SET {0}_lock_date = coalesce(s.max, s.min)
            FROM (SELECT company_id,
                         max(CASE WHEN state='done' THEN date_stop ELSE NULL END),
                         min(CASE WHEN state='draft' THEN date_start - interval '1 day' ELSE NULL END)
                    FROM account_{0}
                GROUP BY company_id) s
           WHERE s.company_id = c.id
        """.format(tbl))
