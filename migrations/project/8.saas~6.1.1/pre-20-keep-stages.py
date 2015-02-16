# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr, 'project.project_tt_cancel', 'project.project_stage_3')

    xids = "analysis specification design development testing merge deployment".split()
    xids = tuple('project_tt_' + x for x in xids)
    cr.execute("""
        UPDATE ir_model_data d
           SET noupdate=true
         WHERE module='project'
           AND model='project.task.type'
           AND name IN %s
           AND EXISTS (SELECT 1 FROM project_task WHERE stage_id = d.res_id)
    """, [xids])
