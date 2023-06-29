# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    additional_where_cond = ""
    if util.column_exists(cr, "project_project", "is_fsm"):
        # then does not take into account the fsm projects in the both queries above
        additional_where_cond = "AND pp.is_fsm IS FALSE"
    cr.execute(
        f"""
      UPDATE project_project pp
         SET allow_billable = TRUE
       WHERE pp.partner_id IS NOT NULL
         AND pp.allow_billable IS FALSE
         {additional_where_cond}
      """
    )

    cr.execute(
        f"""
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
           AND pp.allow_billable IS FALSE
           {additional_where_cond}
        """
    )
