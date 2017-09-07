# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""
        UPDATE project_issue
           SET description = CONCAT('<p>', description, '</p>')
         WHERE description IS NOT NULL
    """)

    util.remove_model(cr, 'project.issue.report')
