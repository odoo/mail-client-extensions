from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_move", "signing_user", "int4")  # avoid computing the column
