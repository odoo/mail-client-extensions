from odoo.upgrade import util


def migrate(cr, version):

    # === PAYMENT ACQUIRER === #

    util.remove_field(cr, "payment.acquirer", "adyen_skin_code")
    util.remove_field(cr, "payment.acquirer", "adyen_skin_hmac_key")

    util.create_column(cr, "payment_acquirer", "adyen_api_key", "varchar")
    util.create_column(cr, "payment_acquirer", "adyen_hmac_key", "varchar")
    util.create_column(cr, "payment_acquirer", "adyen_checkout_api_url", "varchar")
    util.create_column(cr, "payment_acquirer", "adyen_recurring_api_url", "varchar")

    # === PAYMENT TRANSACTION === #

    util.create_column(cr, "payment_transaction", "adyen_payment_data", "varchar")

    # === PAYMENT TOKEN === #

    util.create_column(cr, "payment_token", "adyen_shopper_reference", "varchar")

    # === IR UI VIEW === #

    util.remove_view(cr, xml_id="payment_adyen.adyen_form")

    util.rename_xmlid(cr, "payment_adyen.acquirer_form_adyen", "payment_adyen.payment_acquirer_form")
