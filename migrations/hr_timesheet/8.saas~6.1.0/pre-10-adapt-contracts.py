# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.move_field_to_module(cr, 'account.analytic.account', 'invoice_on_timesheets',
                              'account_analytic_analysis', 'hr_timesheet')
    util.create_column(cr, 'account_analytic_account', 'invoice_on_timesheets', 'boolean')

    cr.execute("UPDATE account_analytic_account SET invoice_on_timesheets = use_timesheets")
