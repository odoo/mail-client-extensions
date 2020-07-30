# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):

    queries = []
    # Update account_move from existing account_invoice.
    queries.append(
        """
        UPDATE account_move am
        SET release_to_pay = inv.release_to_pay,
            release_to_pay_manual = inv.release_to_pay_manual,
            force_release_to_pay = inv.force_release_to_pay
        FROM account_invoice inv
        WHERE move_id IS NOT NULL AND am.id = inv.move_id
    """
    )

    # Update account_move_line from existing account_invoice_line.
    queries.append(
        """
        UPDATE account_move_line aml
        SET can_be_paid = invl.can_be_paid
        FROM invl_aml_mapping m, account_invoice_line invl
        WHERE aml.id = m.aml_id AND invl.id = m.invl_id
    """
    )

    util.parallel_execute(cr, queries)
