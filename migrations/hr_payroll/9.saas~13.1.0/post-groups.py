# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.split_group(cr, ['hr.group_hr_user'], 'hr_payroll.group_hr_payroll_user')
    util.split_group(cr, ['hr.group_hr_manager'], 'hr_payroll.group_hr_payroll_manager')
