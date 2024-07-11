from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_journal", "debit_sequence", "boolean")
