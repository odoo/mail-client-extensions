# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
      UPDATE project_project
         SET allow_billable = TRUE
       WHERE partner_id IS NOT NULL
         AND allow_billable IS NOT TRUE
      """
    )

    cr.execute(
        """
        WITH project_task_with_partner AS (
              SELECT project_id
                FROM project_task
               WHERE project_id IS NOT NULL
                 AND partner_id IS NOT NULL
            GROUP BY project_id
        )
        UPDATE project_project pp
           SET allow_billable = TRUE
          FROM project_task_with_partner pt
         WHERE pt.project_id = pp.id
           AND pp.allow_billable IS NOT TRUE
        """
    )
