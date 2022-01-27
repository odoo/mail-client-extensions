# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_gte("13.0") and not util.version_gte("saas~15.2"):
        util.remove_column(cr, "account_fr_fec", "fec_data")
