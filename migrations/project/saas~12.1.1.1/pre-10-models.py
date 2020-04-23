# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("DELETE FROM ir_translation where name='project.project,label_tasks'")

    util.remove_field(cr, "project.project", "percentage_satisfaction_task")
    util.remove_field(cr, "project.project", "percentage_satisfaction_project")
