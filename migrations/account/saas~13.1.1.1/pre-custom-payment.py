# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Custom payment types will be changed to default 'inbound' to allow the payment refactoring to continue,
    # as no payment types other than 'inbound' and 'outbound' will be allowed.
    # The changed rows are stored to undo the changes after the refactoring.
    cr.execute(
        """
        WITH lines AS (
            SELECT id, payment_type
              FROM account_payment
             WHERE payment_type NOT IN ('inbound', 'outbound', 'transfer')
        )
            UPDATE account_payment AS p
               SET payment_type = 'inbound'
              FROM lines l
             WHERE p.id = l.id
         RETURNING p.id, l.payment_type
        """
    )

    util.ENVIRON["account_payment_payment_types"] = cr.fetchall()
