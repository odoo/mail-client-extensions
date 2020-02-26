# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    taxes = "1 2 3 3b 4 5 6 6b 7 8".split()
    for tax in taxes:
        util.remove_record(cr, f"l10n_no.tax{tax}")
