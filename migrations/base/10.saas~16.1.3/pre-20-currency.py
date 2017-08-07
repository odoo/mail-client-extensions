# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("UPDATE res_currency SET rounding=0.01 WHERE rounding <= 0")

    # only keep one rate per day
    cr.execute("""
     DELETE FROM res_currency_rate WHERE id IN (
        SELECT unnest((array_agg(id ORDER BY name))[2:array_length(array_agg(id), 1)])
          FROM res_currency_rate
      GROUP BY currency_id, company_id, name::date
     )
    """)

    util.drop_depending_views(cr, 'res_currency_rate', 'name')
    cr.execute("ALTER TABLE res_currency_rate ALTER COLUMN name TYPE date")

    util.remove_record(cr, 'base.action_currency_form_company')
