# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, 'account_analytic_line', 'validated', 'boolean')

    cr.execute("""
        UPDATE account_analytic_line aal SET validated = 't'
        FROM hr_timesheet_sheet_sheet t
        WHERE t.id = aal.sheet_id
            AND t.state = 'done'
            AND aal.validated iS NULL """)

    cr.execute("UPDATE account_analytic_line SET validated = 'f' WHERE validated IS NULL")