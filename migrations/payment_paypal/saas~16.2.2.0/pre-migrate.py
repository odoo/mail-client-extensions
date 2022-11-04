from odoo.upgrade import util


def migrate(cr, version):
    # === PAYMENT PROVIDER === #

    util.remove_field(cr, "payment.provider", "paypal_seller_account")
    util.remove_field(cr, "payment.provider", "paypal_use_ipn")

    cr.execute("UPDATE payment_provider SET state='disabled' WHERE paypal_pdt_token IS NULL")

    util.remove_view(cr, "payment_paypal.mail_template_paypal_invite_user_to_configure")
