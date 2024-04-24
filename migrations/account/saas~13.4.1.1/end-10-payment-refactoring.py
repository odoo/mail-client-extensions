from odoo.upgrade import util


def migrate(cr, version):

    # ===========================================================
    # Payment-pocalypse (PR: 41301 & 7019)
    # ===========================================================

    cr.execute("DROP TABLE account_payment_pre_backup CASCADE")
    cr.execute("DROP TABLE account_bank_statement_line_pre_backup CASCADE")
    cr.execute("DROP TABLE account_journal_backup CASCADE")

    # these fields come now from the parent account move
    util.remove_column(cr, "account_bank_statement_line", "date")
    util.remove_column(cr, "account_bank_statement_line", "journal_id")
    util.remove_column(cr, "account_bank_statement_line", "ref")
    util.remove_column(cr, "account_bank_statement_line", "company_id")
