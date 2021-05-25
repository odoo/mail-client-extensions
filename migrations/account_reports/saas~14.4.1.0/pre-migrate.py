# -*- coding: utf-8 -*-
from odoo.upgrade import util

def migrate(cr, version):
    # ===========================================================
    # Task 2463889 : Tax Units
    # ===========================================================
    cr.execute("""
        DELETE
        FROM ir_config_parameter
        WHERE key = 'account_tax_report_multi_company'
        RETURNING value
    """)

    param_value = cr.fetchone()

    if param_value:
        util.add_to_migration_reports(
            "Your database was using multi-company tax reports. "
            "This feature has been replaced by tax units; you will have to create them.",
            "Accounting",
        )
