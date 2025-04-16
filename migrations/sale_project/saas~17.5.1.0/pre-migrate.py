from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sale_order", "project_id", "int4")
    util.explode_execute(
        cr,
        """
        WITH unique_projects AS (
            SELECT account_id,
                   MIN(id) AS project_id
              FROM project_project
             WHERE account_id IS NOT NULL
          GROUP BY account_id
            HAVING COUNT(*) = 1
        )
        UPDATE sale_order so
           SET project_id = up.project_id
          FROM unique_projects up
         WHERE so.analytic_account_id = up.account_id
           AND so.project_id IS NULL
        """,
        table="sale_order",
        alias="so",
    )
