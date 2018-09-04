# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "account.budget.post", "crossovered_budget_line")
    util.rename_field(cr, "crossovered.budget", "creating_user_id", "user_id")

    util.create_column(cr, "crossovered_budget_lines", "crossovered_budget_state", "varchar")
    cr.execute("""
        UPDATE crossovered_budget_lines l
           SET crossovered_budget_state = b.state
          FROM crossovered_budget b
         WHERE b.id = l.crossovered_budget_id
    """)
