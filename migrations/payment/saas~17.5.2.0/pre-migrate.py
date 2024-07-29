from odoo.upgrade import util


def migrate(cr, version):
    util.change_field_selection_values(cr, "payment.method", "support_refund", {None: "none"})
    util.rename_xmlid(cr, "payment.payment_method_emi", "payment.payment_method_emi_india")
    util.remove_field(cr, "payment.provider.onboarding.wizard", "paypal_pdt_token")
