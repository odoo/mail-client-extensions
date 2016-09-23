# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'project_task', 'total_hours_spent', 'double precision')
    util.create_column(cr, 'project_task', 'children_hours', 'double precision')
    cr.execute("UPDATE project_task SET total_hours_spent = COALESCE(effective_hours, 0) + COALESCE(children_hours, 0)"
