# -*- coding: utf-8 -*-


def migrate(cr, version):

    # ===========================================================
    # Payment-pocalypse (PR: 41301 & 7019)
    # ===========================================================

    cr.execute("DROP TABLE account_payment_pre_backup CASCADE")
    cr.execute("DROP TABLE account_bank_statement_line_pre_backup CASCADE")
