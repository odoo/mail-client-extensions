# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""
        UPDATE project_project p
           SET use_pads = id IN (SELECT project_id
                                   FROM project_task
                                  WHERE id <= %s)
    """, [util.ENVIRON.get('issue_offset', 0)])
