# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'project.task', 'delay_hours')
    # odoo/odoo@2ac5888a8d1f8b2bac89314be1e846106c077cca
    util.remove_field(cr, 'project.task', 'total_hours')
    util.rename_field(cr, 'project.task', 'children_hours', 'subtask_effective_hours')

    util.remove_field(cr, 'report.project.task.user', 'hours_delay')
    util.remove_field(cr, 'report.project.task.user', 'total_hours')
