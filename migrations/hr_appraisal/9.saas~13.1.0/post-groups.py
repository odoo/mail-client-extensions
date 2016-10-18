# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.split_group(cr, ['hr.group_hr_user'], 'hr_appraisal.group_hr_appraisal_user')
    util.split_group(cr, ['hr.group_hr_manager'], 'hr_appraisal.group_hr_appraisal_manager')
