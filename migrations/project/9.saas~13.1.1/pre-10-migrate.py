# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.delete_model(cr, 'project.task.history')
    util.delete_model(cr, 'project.task.history.cumulative')

    util.rename_xmlid(cr,
                      'project.edit_project_simplified',
                      'project.project_project_view_form_simpliefied')
