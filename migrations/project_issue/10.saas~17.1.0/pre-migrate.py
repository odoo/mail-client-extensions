# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # If 'project_issue' module is not installed and 'project' is installed
    # That time need to check table 'project_issue' is exist
    # Because Symlinks file 'pre-00-17-issues.py' use in 'project' module
    if util.table_exists(cr, "project_issue"):
        cr.execute("""
            UPDATE project_issue
               SET description = {}
             WHERE description IS NOT NULL
        """.format(util.pg_text2html('description')))

    util.remove_model(cr, 'project.issue.report')
