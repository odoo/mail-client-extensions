from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    util.rename_field(cr, "pos.payment", *eb("viva_{wallet,com}_session_id"))
    util.rename_field(cr, "pos.payment.method", *eb("viva_{wallet,com}_merchant_id"))
    util.rename_field(cr, "pos.payment.method", *eb("viva_{wallet,com}_api_key"))
    util.rename_field(cr, "pos.payment.method", *eb("viva_{wallet,com}_client_id"))
    util.rename_field(cr, "pos.payment.method", *eb("viva_{wallet,com}_client_secret"))
    util.rename_field(cr, "pos.payment.method", *eb("viva_{wallet,com}_terminal_id"))
    util.rename_field(cr, "pos.payment.method", *eb("viva_{wallet,com}_bearer_token"))
    util.rename_field(cr, "pos.payment.method", *eb("viva_{wallet,com}_webhook_verification_key"))
    util.rename_field(cr, "pos.payment.method", *eb("viva_{wallet,com}_latest_response"))
    util.rename_field(cr, "pos.payment.method", *eb("viva_{wallet,com}_test_mode"))
    util.rename_field(cr, "pos.payment.method", *eb("viva_{wallet,com}_webhook_endpoint"))
    util.rename_xmlid(cr, *eb("pos_viva_com.pos_payment_method_view_form_inherit_pos_viva_{wallet,com}"))
