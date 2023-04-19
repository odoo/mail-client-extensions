from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "payment.payment_transaction_user_rule")
    util.remove_record(cr, "payment.payment_transaction_all")
    util.remove_record(cr, "payment.payment_transaction_user")
