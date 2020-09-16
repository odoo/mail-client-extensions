# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Reconciliation models refactoring (Task 2182807)
    util.create_column(cr, "account_reconcile_model", "past_months_limit", "int4", default=18)
    util.create_column(cr, "account_tax", "tax_scope", "varchar")
