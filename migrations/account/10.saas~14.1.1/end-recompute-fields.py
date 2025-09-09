# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    query = "SELECT id FROM account_invoice_tax WHERE base IS NULL"
    util.recompute_fields(cr, "account.invoice.tax", ["base"], query=query)
