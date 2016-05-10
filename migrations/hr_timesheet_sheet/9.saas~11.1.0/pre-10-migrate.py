# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.force_noupdate(cr, 'hr_timesheet_sheet.menu_act_hr_timesheet_sheet_form_my_current', False)
