# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr,
                      'pad_project.view_task_form_with_pad',
                      'pad_project.view_task_form2_inherit_pad_project')
