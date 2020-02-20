# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""
    SELECT id
      FROM account_payment
     WHERE payment_type NOT IN ('inbound','outbound')
    """)
    if cr.rowcount:
        raise util.MigrationError("Only 'inbound' and 'outbound' are valid values for payment_type on account_payment.")
