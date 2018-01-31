# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        UPDATE project_project p
           SET use_pads = NOT EXISTS(SELECT id
                                       FROM project_task
                                      WHERE project_id = p.id
                                        AND x_original_issue_id IS NOT NULL)
    """)
