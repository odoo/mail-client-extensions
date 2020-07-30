# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    pv = util.parse_version
    if pv(version) >= pv("saas~12.4"):
        # This script is also linked from `l10n_mx_edi@saas~12.5` (modules merged)
        # But should only be called for databases older than saas~12.4
        return

    util.create_column(cr, "account_move_line", "l10n_mx_edi_customs_number", "varchar")
