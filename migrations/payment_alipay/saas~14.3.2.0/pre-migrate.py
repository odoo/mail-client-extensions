from odoo.upgrade import util


def migrate(cr, version):

    # === IR UI VIEW === #

    util.remove_view(cr, xml_id="payment_alipay.alipay_form")

    util.rename_xmlid(
        cr, "payment_alipay.payment_acquirer_view_form_inherit_payment_alipay", "payment_alipay.payment_acquirer_form"
    )
