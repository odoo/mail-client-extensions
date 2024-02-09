from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "payment.pay_meth_link")

    util.rename_xmlid(cr, "payment.transaction_status", "payment.state_header")

    util.remove_field(cr, "payment.provider", "show_credentials_page")
    util.remove_field(cr, "payment.provider", "show_allow_tokenization")
    util.remove_field(cr, "payment.provider", "show_allow_express_checkout")
    util.remove_field(cr, "payment.provider", "show_pre_msg")
    util.remove_field(cr, "payment.provider", "show_pending_msg")
    util.remove_field(cr, "payment.provider", "show_auth_msg")
    util.remove_field(cr, "payment.provider", "show_done_msg")
    util.remove_field(cr, "payment.provider", "show_cancel_msg")
    util.remove_field(cr, "payment.provider", "require_currency")
