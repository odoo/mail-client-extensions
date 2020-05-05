# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
            ALTER TABLE account_analytic_tag_account_reconcile_model_rel
              RENAME TO account_reconcile_model_analytic_tag_rel
        """
    )
    util.fixup_m2m(
        cr,
        "account_reconcile_model_analytic_tag_rel",
        "account_reconcile_model",
        "account_analytic_tag",
        "account_reconcile_model_id",
        "account_analytic_tag_id",
    )
