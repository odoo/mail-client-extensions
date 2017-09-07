# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr,
                      'hr_holidays.report_holidays_summary',
                      'hr_holidays.action_report_holidaysummary')
    util.rename_xmlid(cr,
                      'hr_holidays.menu_account_central_journal',
                      'hr_holidays.menu_hr_holidays_summary_dept')
