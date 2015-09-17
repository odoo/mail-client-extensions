# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'account_analytic_line', 'is_timesheet', 'boolean')
    if not util.get_index_on(cr, 'hr_analytic_timesheet', 'line_id'):
        cr.execute("CREATE INDEX ON hr_analytic_timesheet(line_id)")
    cr.execute("""
        UPDATE account_analytic_line l
           SET is_timesheet = EXISTS(SELECT 1 FROM hr_analytic_timesheet WHERE line_id=l.id)
    """)

    util.delete_model(cr, 'hr.sign.out.project')
    util.delete_model(cr, 'hr.sign.in.project')
