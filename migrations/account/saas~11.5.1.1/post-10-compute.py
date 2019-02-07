# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.recompute_fields(cr, "res.currency", ["decimal_places"])
    # for some reason, some related fields from the past might not be set correctly
    # (3 databases so far had the problem), so we make sure the company_id field is
    # correctly set on sale and invoice lines otherwise the currency computation crashes
    cr.execute("""
        UPDATE account_invoice_line  ail
            SET company_id=ai.company_id
            FROM account_invoice ai
            WHERE ai.id=ail.invoice_id AND
                  ail.company_id IS NULL
    """)
