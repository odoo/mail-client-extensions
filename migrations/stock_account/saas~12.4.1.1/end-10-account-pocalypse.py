# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
            UPDATE account_move_line aml
               SET is_anglo_saxon_line = 'f'
             WHERE NOT aml.exclude_from_invoice_tab
               AND is_anglo_saxon_line IS NOT FALSE
            """,
            table="account_move_line",
            alias="aml",
        ),
    )
