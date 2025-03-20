from odoo.upgrade import util


def migrate(cr, version):
    additional_where_cond = ""
    if util.column_exists(cr, "project_project", "is_fsm"):
        # then does not take into account the fsm projects in the both queries above
        additional_where_cond = "AND pp.is_fsm IS FALSE"
    timesheet_cond = ""

    if util.module_installed(cr, "industry_fsm_sale"):
        # match the `project_project_timesheet_product_required_if_billable_and_time` constraint
        timesheet_cond = "AND (pp.timesheet_product_id IS NOT NULL OR pp.allow_timesheets=FALSE)"
    else:
        # Remove the constraint if uninstalled.
        util.remove_constraint(
            cr, "project_project", "project_project_timesheet_product_required_if_billable_and_time", warn=False
        )

    query = util.format_query(
        cr,
        """
      UPDATE project_project pp
         SET allow_billable = TRUE
       WHERE pp.partner_id IS NOT NULL
         AND pp.allow_billable IS FALSE
         {}
         {}
      """,
        util.SQLStr(additional_where_cond),
        util.SQLStr(timesheet_cond),
    )
    cr.execute(query)

    query = util.format_query(
        cr,
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
           AND pp.allow_billable IS FALSE
         {}
         {}
      """,
        util.SQLStr(additional_where_cond),
        util.SQLStr(timesheet_cond),
    )
    cr.execute(query)
