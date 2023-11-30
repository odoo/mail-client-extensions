# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_module(cr, "mrp_subonctracting_landed_costs", "mrp_subcontracting_landed_costs")

    if util.has_enterprise():
        util.rename_module(cr, "account_bacs", "l10n_uk_bacs")
