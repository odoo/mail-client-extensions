# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""
        UPDATE project_project p
           SET use_pads = id NOT IN (SELECT project_id
                                       FROM project_task
                                      WHERE id > %s
                                   GROUP BY project_id)
    """, [util.ENVIRON.get('issue_offset', 0)])
