from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "pos_iot.view_payment_method_pos_iot_user_form")
    util.remove_field(cr, "pos.payment.method", "payment_terminal_ids")
    util.remove_field(cr, "res.config.settings", "worldline_payment_terminal")
    util.remove_field(cr, "res.config.settings", "ingenico_payment_terminal")
