# -*- coding: utf-8 -*-
def migrate(cr, version):
    cr.execute("SELECT count(id) FROM res_company")
    company_count, = cr.fetchone()
    cr.execute("SELECT company_id FROM res_currency GROUP BY company_id")
    if cr.rowcount == 1 or company_count == 1:
        cr.execute("UPDATE res_currency SET company_id=NULL")
