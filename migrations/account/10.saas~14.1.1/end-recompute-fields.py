# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("SELECT id FROM account_invoice_tax WHERE base IS NULL")
    ids = [row[0] for row in cr.fetchall()]
    util.recompute_fields(cr, "account.invoice.tax", ["base"], ids=ids)
