from odoo.upgrade import util


def migrate(cr, version):
    util.alter_column_type(
        cr, "account_bank_statement_line_transient", "transaction_details", "jsonb", using="{0}::jsonb"
    )
