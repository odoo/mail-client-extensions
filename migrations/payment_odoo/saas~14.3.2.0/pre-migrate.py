from odoo.upgrade import util


def migrate(cr, version):

    # === PAYMENT ACQUIRER === #

    util.change_field_selection_values(cr, "payment.provider", "provider", {"odoo_adyen": "odoo"})

    # === PAYMENT TOKEN === #

    util.rename_field(cr, "payment.token", "odoo_adyen_payment_method_type", "odoo_payment_method_type")

    # === IR UI VIEW === #

    util.remove_view(cr, xml_id="payment_odoo.odoo_by_adyen_form")

    util.rename_xmlid(cr, "payment_odoo.acquirer_form_odoo_by_adyen", "payment_odoo.payment_acquirer_form")
