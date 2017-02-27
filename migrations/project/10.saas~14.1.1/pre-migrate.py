# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr, 'project.activate_sample_project',
                      'project.ir_actions_server_project_sample')
