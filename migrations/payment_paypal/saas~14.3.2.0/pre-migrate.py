from odoo.upgrade import util


def migrate(cr, version):

    # === PAYMENT TRANSACTION === #

    util.rename_field(cr, "payment.transaction", "paypal_txn_type", "paypal_type")

    # === IR UI VIEW === #

    util.remove_view(cr, xml_id="payment_paypal.paypal_form")

    util.rename_xmlid(cr, "payment_paypal.acquirer_form_paypal", "payment_paypal.payment_acquirer_form")
    util.rename_xmlid(cr, "payment_paypal.transaction_form_paypal", "payment_paypal.payment_transaction_form")
