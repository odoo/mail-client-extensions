# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("UPDATE project_task_type SET legend_blocked='Blocked' WHERE legend_blocked IS NULL")
    cr.execute("UPDATE project_task_type SET legend_done='Ready for Next Stage' WHERE legend_done IS NULL")
    cr.execute("UPDATE project_task_type SET legend_normal='In Progress' WHERE legend_normal IS NULL")

    util.remove_field(cr, 'project.config.settings', 'generate_project_alias')
