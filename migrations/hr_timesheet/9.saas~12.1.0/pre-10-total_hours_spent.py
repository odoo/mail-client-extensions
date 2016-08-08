# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'project_task', 'total_hours_spent', 'double precision')
    cr.execute("UPDATE project_task SET total_hours_spent = effective_hours + children_hours")
