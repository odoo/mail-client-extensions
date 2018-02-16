# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    p = 'l10n_in_hr_payroll.'
    util.rename_xmlid(cr, p + 'hr_salary_bymonth', p + 'action_report_hrsalarybymonth')
    util.rename_xmlid(cr, p + 'yearly_salary', p + 'action_report_hryearlysalary')
