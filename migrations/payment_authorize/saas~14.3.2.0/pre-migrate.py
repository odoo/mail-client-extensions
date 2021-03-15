from odoo.upgrade import util


def migrate(cr, version):

    # === PAYMENT ACQUIRER === #

    util.create_column(cr, "payment_acquirer", "authorize_currency_id", "int4")

    # === PAYMENT TOKEN === #

    util.remove_field(cr, "payment.token", "save_token")

    # === IR UI VIEW === #

    util.remove_view(cr, xml_id="payment_authorize.authorize_form")
    util.remove_view(cr, xml_id="payment_authorize.payment_authorize_redirect")
    util.remove_view(cr, xml_id="payment_authorize.authorize_s2s_form")

    util.rename_xmlid(cr, "payment_authorize.acquirer_form_authorize", "payment_authorize.payment_acquirer_form")
    util.rename_xmlid(cr, "payment_authorize.token_form_authorize_net", "payment_authorize.payment_token_form")
