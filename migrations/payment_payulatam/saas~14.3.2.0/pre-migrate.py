from odoo.upgrade import util


def migrate(cr, version):

    # === IR UI VIEW === #

    util.remove_view(cr, xml_id="payment_payulatam.payulatam_form")

    util.rename_xmlid(
        cr,
        "payment_payulatam.payment_acquirer_form_inherit_payment_payulatam",
        "payment_payulatam.payment_acquirer_form",
    )
