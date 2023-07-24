from psycopg2 import sql

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "project.task.create.timesheet")
    util.remove_field(cr, "project.task", "display_timer_start_secondary")

    if util.column_exists(cr, "account_analytic_line", "helpdesk_ticket_id"):
        parent_res_model_query = """
            CASE
                WHEN AAL.helpdesk_ticket_id IS NOT NULL
                THEN 'helpdesk.ticket'
                ELSE 'project.task'
            END
        """
        parent_res_id_query = """
            CASE
                WHEN AAL.helpdesk_ticket_id IS NOT NULL
                THEN AAL.helpdesk_ticket_id
                ELSE AAL.task_id
             END
        """
        where_clause = """
            COALESCE(AAL.helpdesk_ticket_id, AAL.task_id) IS NOT NULL
        """
    else:
        parent_res_model_query = "'project.task'"
        parent_res_id_query = "AAL.task_id"
        where_clause = "AAL.task_id IS NOT NULL"
    util.explode_execute(
        cr,
        util.format_query(
            cr,
            """
                UPDATE timer_timer t
                   SET parent_res_model = {parent_res_model},
                       parent_res_id = {parent_res_id}
                  FROM account_analytic_line AAL
                  WHERE t.res_model = 'account.analytic.line'
                    AND AAL.id = t.res_id
                    AND {where_clause}
            """,
            parent_res_model=sql.SQL(parent_res_model_query),
            parent_res_id=sql.SQL(parent_res_id_query),
            where_clause=sql.SQL(where_clause),
        ),
        table="timer_timer",
        alias="t",
    )
