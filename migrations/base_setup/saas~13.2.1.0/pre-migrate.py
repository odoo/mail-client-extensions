# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_field(cr, "res.config.settings", *eb("module_{,account_}inter_company_rules"))
