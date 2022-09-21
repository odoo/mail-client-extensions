# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.column_exists(cr, "account_account", "internal_type"):
        # < 16
        cond = "internal_type IN ('payable', 'receivable')"
    else:
        cond = "account_type IN ('asset_receivable', 'liability_payable')"

    query = "UPDATE account_account SET reconcile = true WHERE {} AND reconcile = false".format(cond)
    cr.execute(query)
