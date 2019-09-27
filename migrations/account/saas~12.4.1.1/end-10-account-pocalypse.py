# -*- coding: utf-8 -*-


def migrate(cr, version):
    # cr.execute("DROP TABLE account_invoice CASCADE")
    # cr.execute("DROP TABLE account_invoice_line CASCADE")
    # cr.execute("DROP TABLE account_invoice_tax CASCADE")
    cr.execute("DROP TABLE IF EXISTS invl_aml_mapping CASCADE")
    cr.execute("DROP TABLE IF EXISTS account_voucher CASCADE")
    cr.execute("DROP TABLE IF EXISTS account_voucher_line CASCADE")
