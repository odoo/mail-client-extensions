# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE account_account_type
           SET internal_group = 'off_balance'
         WHERE id = %s
    """,
        [util.ref(cr, "l10n_gr.account_type_other")],
    )
