from odoo.upgrade import util


def migrate(cr, version):

    # === PAYMENT ACQUIRER === #

    util.remove_field(cr, "payment.acquirer", "ogone_alias_usage")

    # === IR UI VIEW === #

    util.remove_view(cr, xml_id="payment_ogone.ogone_form")
    util.remove_view(cr, xml_id="payment_ogone.ogone_s2s_form")

    util.rename_xmlid(cr, "payment_ogone.acquirer_form_ogone", "payment_ogone.payment_acquirer_form")
