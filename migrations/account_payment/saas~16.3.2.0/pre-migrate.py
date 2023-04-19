from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "account_payment.payment_transaction_billing_rule")
