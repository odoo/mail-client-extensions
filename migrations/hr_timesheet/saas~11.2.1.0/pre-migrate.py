# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'project.task', 'delay_hours')
    util.rename_field(cr, 'project.task', 'children_hours', 'subtask_effective_hours')

    util.remove_field(cr, 'report.project.task.user', 'hours_delay')
    util.remove_field(cr, 'report.project.task.user', 'total_hours')
