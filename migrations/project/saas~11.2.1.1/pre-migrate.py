# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_model(cr, 'project.task.merge.wizard')
    util.remove_view(cr, 'project.mail_template_task_merge')

    util.remove_field(cr, 'project.project', 'subtask_project_id')
    util.remove_field(cr, 'project.task', 'subtask_project_id')
