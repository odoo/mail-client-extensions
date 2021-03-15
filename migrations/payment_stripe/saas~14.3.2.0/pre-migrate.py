from odoo.upgrade import util


def migrate(cr, version):

    # === PAYMENT ACQUIRER === #

    util.remove_field(cr, "payment.acquirer", "stripe_image_url")

    # === PAYMENT TRANSACTION === #

    util.remove_field(cr, "payment.transaction", "stripe_payment_intent_secret")

    # === IR UI VIEW === #

    util.remove_view(cr, xml_id="payment_stripe.stripe_form")
    util.remove_view(cr, xml_id="payment_stripe.stripe_s2s_form")

    util.rename_xmlid(cr, "payment_stripe.acquirer_form_stripe", "payment_stripe.payment_acquirer_form")
