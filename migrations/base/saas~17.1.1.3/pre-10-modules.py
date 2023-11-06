# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    if util.has_enterprise():
        util.rename_module(cr, "account_bacs", "l10n_uk_bacs")
