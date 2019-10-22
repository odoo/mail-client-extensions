# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_field(cr, "pos.config", "iotbox_id", "iface_printer_id")
    util.create_column(cr, "pos_config", "iface_display_id", "int4")
    util.create_column(cr, "pos_config", "iface_scale_id", "int4")
    util.create_column(cr, "pos_payment_method", "iot_device_id", "int4")

    util.remove_field(cr, "account.journal", "use_payment_terminal")
    util.remove_field(cr, "pos.config", "proxy_ip")
    util.remove_field(cr, "pos.config", "iface_payment_terminal")
