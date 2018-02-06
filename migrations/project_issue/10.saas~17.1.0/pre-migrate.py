# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""
        UPDATE project_issue
           SET description = {}
         WHERE description IS NOT NULL
    """.format(util.pg_text2html('description')))

    util.remove_model(cr, 'project.issue.report')
