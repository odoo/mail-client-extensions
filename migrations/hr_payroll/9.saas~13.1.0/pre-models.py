# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.drop_workflow(cr, 'hr.payslip')
    util.delete_model(cr, 'report.hr_payroll.report_payslip')
