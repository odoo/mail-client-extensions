from odoo.upgrade import util


def migrate(cr, version):
    # create empty column for new install
    util.create_column(cr, "account_bank_statement_line", "online_link_id", "int4")
