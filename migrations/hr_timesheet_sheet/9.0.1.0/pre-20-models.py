# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'account_analytic_line', 'sheet_id', 'int4')
    cr.execute("""
        UPDATE account_analytic_line l
           SET sheet_id = h.id
           FROM hr_timesheet_sheet_sheet h
         WHERE h.date_to >= l.date AND h.date_from <= l.date AND h.user_id = l.user_id AND l.is_timesheet = 't'
    """)

