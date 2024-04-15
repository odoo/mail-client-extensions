from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "account_payment_term", "currency_id")
