# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_analytic_line", "validated", "boolean", default=False)

    if util.table_exists(cr, "hr_timesheet_sheet_sheet"):
        query = """
            UPDATE account_analytic_line aal
               SET validated = 't'
              FROM hr_timesheet_sheet_sheet t
             WHERE t.id = aal.sheet_id
                AND t.state = 'done'
        """
        util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_analytic_line", alias="aal"))
