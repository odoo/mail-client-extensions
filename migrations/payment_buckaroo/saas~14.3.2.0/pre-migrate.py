from odoo.upgrade import util


def migrate(cr, version):

    # === PAYMENT ACQUIRER === #

    util.rename_field(cr, "payment.acquirer", "brq_websitekey", "buckaroo_website_key")
    util.rename_field(cr, "payment.acquirer", "brq_secretkey", "buckaroo_secret_key")

    # === IR UI VIEW === #

    util.remove_view(cr, xml_id="payment_buckaroo.buckaroo_form")

    util.rename_xmlid(cr, "payment_buckaroo.acquirer_form_buckaroo", "payment_buckaroo.payment_acquirer_form")
