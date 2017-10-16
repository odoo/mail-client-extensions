# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'project_project', 'use_pads', 'boolean')
    cr.execute("""
        UPDATE project_project p
           SET use_pads = NOT EXISTS(SELECT id
                                       FROM project_task
                                      WHERE project_id = p.id
                                        AND x_original_issue_id IS NOT NULL)
    """)
