# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT 1
          FROM ir_sequence
         WHERE code = 'account.reconcile'
               AND company_id IS NULL
         LIMIT 1
    """
    )

    if not cr.rowcount:
        env = util.env(cr)
        env["ir.sequence"].create(
            {"name": "Account reconcile sequence", "code": "account.reconcile", "prefix": "A", "company_id": False}
        )
