# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_move_line", "move_name", "varchar")
    util.create_column(cr, "account_move_line", "parent_state", "varchar")
    util.create_column(cr, "account_move_line", "journal_id", "int4")
    util.create_column(cr, "account_move_line", "company_id", "int4")

    util.parallel_execute(
        cr,
        util.explode_query(
            cr,
            """
            UPDATE account_move_line aml
               SET move_name=am.name,
                   parent_state=am.state,
                   journal_id=am.journal_id,
                   company_id=am.company_id
              FROM account_move am
             WHERE am.id=aml.move_id
            """,
            prefix="aml.",
        ),
    )
