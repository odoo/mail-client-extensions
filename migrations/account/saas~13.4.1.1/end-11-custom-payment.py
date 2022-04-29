# -*- coding: utf-8 -*-
import psycopg2

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # The custom payment types are restored to their original values
    payments = util.ENVIRON["account_payment_payment_types"]
    if payments:
        psycopg2.extras.execute_values(
            cr._obj,
            """
            UPDATE account_payment AS p
               SET payment_type = c.payment_type
              FROM (VALUES %s) AS c(id, payment_type)
             WHERE p.id = c.id
            """,
            payments,
        )
        util.add_to_migration_reports(
            message="<details><summary>"
            "Your database contains custom payment types that are computed using custom code. "
            "Payment is refactored in version 14 so payments need to be recomputed during the upgrade."
            "Your custom payment types have been temporarily converted to standard inbound payments."
            "You might need to recompute these payments with your custom code."
            "</summary></details>",
            category="Custom payment types",
            format="html",
        )
