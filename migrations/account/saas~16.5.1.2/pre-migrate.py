# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.alter_column_type(
        cr, "account_report", "filter_account_type", "varchar", using="CASE WHEN {0} THEN 'both' ELSE 'disabled' END"
    )
    util.remove_view(cr, "account.view_account_analytic_line_filter_inherit")

    cr.execute("DROP INDEX IF EXISTS account_move_line__unreconciled_index")
    cr.execute(
        """
        CREATE INDEX "account_move_line__unreconciled_index"
                  ON "account_move_line"
               USING btree (account_id, partner_id)
                  -- Match exactly how the ORM converts domains to ensure the query planner uses it
               WHERE (reconciled IS NULL OR reconciled = false OR reconciled IS NOT true) AND parent_state = 'posted'
    """
    )
