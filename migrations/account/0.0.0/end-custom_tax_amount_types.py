# -*- coding: utf-8 -*-
import psycopg2

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # restore custom tax amount types modified in pre-custom_tax_amount_types.py
    taxes = util.ENVIRON["account_tax_amount_types"]

    if taxes:
        psycopg2.extras.execute_values(
            cr._obj,
            """
            UPDATE account_tax t
               SET amount_type = l.amount_type, amount = l.amount
              FROM (VALUES %s) AS l(id, amount_type, amount)
             WHERE t.id = l.id
            """,
            taxes,
        )

        util.add_to_migration_reports(
            message="Your database contains custom taxes that are computed using custom code. "
            "As taxes may be recomputed during upgrade, these custom taxes has been temporary converted "
            "into standard taxes of 0.01% and then restored to their original custom type. "
            "To get correct tax amounts, you have to recompute these custom taxes with your custom code.",
            category="Custom taxes",
        )
