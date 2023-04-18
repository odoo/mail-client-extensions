# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "l10n_in_upi", "l10n_in")
    if util.has_enterprise():
        util.remove_module(cr, "industry_fsm_forecast")
