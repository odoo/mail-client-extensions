# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def _db_openerp(cr, version):
    cr.execute("""
        UPDATE ir_model_fields
           SET compute = 'for task in self:\n    task["x_original_issue_id"] = str(task.id)',
               field_description = 'OPW',
               depends='create_date'
         WHERE name = 'x_original_issue_id'
           AND model = 'project.task'
    """)

def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {
        '8851207e-1ff9-11e0-a147-001cc0f2115e': _db_openerp,
    })
