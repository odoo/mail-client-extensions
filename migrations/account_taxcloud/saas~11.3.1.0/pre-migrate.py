# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    for f in {"tic_category_ids", "state_ids", "zip_codes"}:
        util.remove_field(cr, "account.fiscal.position.tax.template", f)
        util.remove_field(cr, "account.fiscal.position.tax", f)
