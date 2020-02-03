# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    for c in range(1, 17):
        util.remove_record(cr, "l10n_pl.CA%02d" % c)

    util.delete_unused(cr, "account_account_type", ["l10n_pl.account_type_nonbalance", "l10n_pl.account_type_tax"])
