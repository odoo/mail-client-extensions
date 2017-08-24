# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'hr.employee', 'account_id')

    util.create_column(cr, 'account_analytic_line', 'timesheet_invoice_type', 'varchar')
    util.create_column(cr, 'account_analytic_line', 'timesheet_invoice_id', 'int4')
    util.create_column(cr, 'account_analytic_line', 'timesheet_revenue', 'numeric')
