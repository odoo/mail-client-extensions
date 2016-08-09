# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr,
                      'website_project_issue.issues_followup',
                      'website_project_issue.my_issues_issue')
