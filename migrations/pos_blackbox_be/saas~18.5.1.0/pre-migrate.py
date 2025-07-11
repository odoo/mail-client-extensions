from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "iot.reload.drivers.wizard")

    util.remove_record(cr, "pos_blackbox_be.reload_iot_after_install")
    util.remove_record(cr, "pos_blackbox_be.action_load_driver")
