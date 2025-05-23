from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "pos_iot_six.add_six_terminal", "iot_box_url")
