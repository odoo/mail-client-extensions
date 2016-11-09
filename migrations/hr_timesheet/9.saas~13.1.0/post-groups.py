# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.split_group(cr, ['hr.group_hr_user'], 'hr_timesheet.group_hr_timesheet_user')
