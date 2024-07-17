from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "pos_self_order.pos_self_order_kiosk_read_only_form_dialog")
