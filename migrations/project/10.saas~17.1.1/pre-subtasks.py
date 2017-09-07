# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.move_field_to_module(cr, 'project.project', 'subtask_project_id',
                              'hr_timesheet', 'project')
    for field in 'parent_id child_ids subtask_project_id subtask_count'.split():
        util.move_field_to_module(cr, 'project.task', field, 'hr_timesheet', 'project')
