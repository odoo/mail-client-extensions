# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Migrate values from account_invoice to account_move.
    cr.execute(
        """
        UPDATE account_move am
        SET auto_generated = inv.auto_generated,
            auto_invoice_id = auto_invoice.move_id
        FROM account_invoice inv
        JOIN account_invoice auto_invoice ON auto_invoice.id = inv.auto_invoice_id
        WHERE inv.move_id = am.id
    """
    )
