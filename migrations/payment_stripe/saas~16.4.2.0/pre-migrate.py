from odoo.upgrade import util


def migrate(cr, version):
    query = """
        UPDATE payment_transaction
        SET provider_reference = stripe_payment_intent
        WHERE stripe_payment_intent <> ''
    """
    util.explode_execute(cr, query, table="payment_transaction")
    util.remove_field(cr, "payment.transaction", "stripe_payment_intent")
