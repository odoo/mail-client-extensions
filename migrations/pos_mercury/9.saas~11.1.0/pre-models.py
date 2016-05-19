# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("UPDATE account_bank_statement_line SET mercury_invoice_no = NULL WHERE mercury_invoice_no=0")
    cr.execute("ALTER TABLE account_bank_statement_line ALTER COLUMN mercury_invoice_no TYPE varchar")
