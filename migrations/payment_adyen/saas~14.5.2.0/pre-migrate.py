from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "payment_acquirer", "adyen_client_key", "varchar")
    util.remove_field(cr, "payment.transaction", "adyen_payment_data")
