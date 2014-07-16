# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # remove unused menus
    # they were no longer used in 7.0 but a security file tried to add groups
    # to these non existing menus and thus created the records
    util.remove_record(cr, 'mrp.mrp_Sched_all')
    util.remove_record(cr, 'survey.menu_answer_surveys')
    util.remove_record(cr, 'survey.menu_define_survey')

