# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Replace custom tax amount types by standard ones, to avoid tax calculation exception
    # (the custom _compute_amount method is a part of the custom module and so it's not available).
    # A not-null amount is used to avoid errors during tax upgrade in saas-12.3.
    # These custom amount types are restored in end-custom_tax_amount_types.py
    cr.execute(
        """
        WITH lines AS (
            SELECT id, amount_type, amount
              FROM account_tax
             WHERE amount_type NOT IN ('fixed', 'percent', 'division', 'code', 'group')
        )
            UPDATE account_tax t
               SET amount_type = 'percent', amount = 0.01
              FROM lines l
             WHERE t.id = l.id
         RETURNING l.id, l.amount_type, l.amount
    """
    )

    util.ENVIRON["account_tax_amount_types"] = cr.fetchall()
