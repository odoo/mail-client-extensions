# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'project_project', 'rating_status', 'varchar')
    util.create_column(cr, 'project_project', 'rating_request_deadline', 'timestamp without time zone')

    cr.execute("""
        WITH stages AS (
            UPDATE mail_template m
               SET model = 'project.task'
              FROM project_task_type t
             WHERE m.id = t.rating_template_id
         RETURNING t.id
        )
        UPDATE project_project p
           SET rating_status = 'stage'
          FROM stages s, project_task_type_rel r
         WHERE p.id = r.project_id
           AND r.type_id = s.id
    """)
    cr.execute("UPDATE project_project SET rating_status = 'no' WHERE rating_status IS NULL")
