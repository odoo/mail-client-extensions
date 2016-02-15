# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("""
        UPDATE account_invoice
           SET reference = concat_ws('_', reference, supplier_invoice_number)
         WHERE supplier_invoice_number IS NOT NULL;
    """)
