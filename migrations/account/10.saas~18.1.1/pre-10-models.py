# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'account_account_tag', 'active', 'boolean')
    cr.execute("UPDATE account_account_tag SET active=true")
    util.create_column(cr, 'account_journal', 'active', 'boolean')
    cr.execute("UPDATE account_journal SET active=true")

    util.create_column(cr, 'account_tax', 'tax_exigibility', 'varchar')
    util.create_column(cr, 'account_tax_template', 'tax_exigibility', 'varchar')

    if util.column_exists(cr, 'account_tax', 'use_cash_basis'):
        # may not exists before saas~14 if module `account_tax_cash_basis` is not installed
        cr.execute("""
            UPDATE account_tax
               SET tax_exigibility = CASE WHEN use_cash_basis = true THEN 'on_payment'
                                          ELSE 'on_invoice'
                                      END
        """)
        util.remove_field(cr, 'account.tax', 'use_cash_basis')
    else:
        cr.execute("UPDATE account_tax SET tax_exigibility='on_invoice'")

    if util.column_exists(cr, 'account_tax_template', 'use_cash_basis'):
        # may not exists before saas~14 if module `account_tax_cash_basis` is not installed
        cr.execute("""
            UPDATE account_tax_template
               SET tax_exigibility = CASE WHEN use_cash_basis = true THEN 'on_payment'
                                          ELSE 'on_invoice'
                                      END
        """)
        util.remove_field(cr, 'account.tax.template', 'use_cash_basis')
    else:
        cr.execute("UPDATE account_tax_template SET tax_exigibility='on_invoice'")

    util.create_column(cr, 'account_invoice_line', 'price_total', 'numeric')    # filled in end-
    util.create_column(cr, 'account_invoice_line', 'is_rounding_line', 'boolean')

    util.create_column(cr, 'account_payment_term', 'sequence', 'int4')
    cr.execute("UPDATE account_payment_term SET sequence=10")

    util.remove_field(cr, 'account.full.reconcile', 'exchange_partial_rec_id')

    cr.execute("UPDATE account_payment SET state='cancelled' WHERE state='cancel'")

    util.remove_model(cr, 'account.invoice.cancel')
