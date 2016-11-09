# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.split_group(cr, ['hr.group_hr_user'], 'hr_recruitment.group_hr_recruitment_user')
    util.split_group(cr, ['hr.group_hr_manager'], 'hr_recruitment.group_hr_recruitment_manager')
