# -*- coding: utf-8 -*-

def migrate(cr, version):
    # remove stale xmlids
    cr.execute("""
        DELETE FROM ir_model_data x
              WHERE module='project'
                AND name='project_project_data'
                AND model='project.project'
                AND NOT EXISTS(SELECT 1 FROM project_project WHERE id=x.res_id)
    """)
