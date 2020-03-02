# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE account_account_type
           SET internal_group = 'off'
         WHERE id IN %s
    """,
        [(util.ref(cr, "l10n_pl.account_type_tax"), util.ref(cr, "l10n_pl.account_type_settlement"))],
    )

    util.delete_unused(cr, *[f"l10n_pl.CA{c:02}" for c in range(1, 17)])
    util.delete_unused(cr, "l10n_pl.account_type_nonbalance")
