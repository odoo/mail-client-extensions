# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr,
                      'website_project_issue_sheet.issues_followup_sheet',
                      'website_project_issue_sheet.my_issues_issue')
