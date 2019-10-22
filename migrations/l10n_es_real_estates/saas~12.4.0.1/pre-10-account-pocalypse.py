# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_move", "l10n_es_real_estate_id", "int4")

    # Migrate values from account_invoice to account_move.
    cr.execute(
        """
        UPDATE account_move am
        SET l10n_es_real_estate_id = inv.l10n_es_real_estate_id
        FROM account_invoice inv
        WHERE inv.move_id = am.id
    """
    )
