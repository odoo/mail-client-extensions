from odoo.upgrade import util


def migrate(cr, version):

    # === IR UI VIEW === #

    util.remove_view(cr, xml_id="payment_payumoney.payumoney_form")

    util.rename_xmlid(
        cr, "payment_payumoney.payment_acquirer_form_payumoney", "payment_payumoney.payment_acquirer_form"
    )
