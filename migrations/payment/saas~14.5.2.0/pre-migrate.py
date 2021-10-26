from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "payment.transaction", "validation_route")
    util.create_column(cr, "account_payment", "source_payment_id", "int4")
    util.create_column(cr, "payment_acquirer", "support_refund", "varchar")
    util.create_column(cr, "payment_transaction", "source_transaction_id", "int4")
    util.delete_unused(cr, "payment.payment_acquirer_odoo")
