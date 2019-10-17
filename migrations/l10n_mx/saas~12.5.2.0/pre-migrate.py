# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    fpt = {1, 3, 5, 6, 7, 9, 10, 11, 12, 14, 15, 16, 20, 21, 22, 23, 24, 28, 29, 30}
    for x in fpt:
        util.remove_record(cr, "l10n_mx.account_fiscal_position_6%02d_fr" % x)
