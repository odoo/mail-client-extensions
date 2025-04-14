from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "pos.config", "available_iot_box_ids", "self_ordering_iot_available_iot_box_ids")
