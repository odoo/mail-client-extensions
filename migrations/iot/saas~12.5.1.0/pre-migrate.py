# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "iot_box", "version", "varchar")
    util.create_column(cr, "iot_box", "company_id", "int4")
    util.create_column(cr, "iot_box", "drivers_auto_update", "boolean")

    cr.execute("UPDATE iot_box SET drivers_auto_update=TRUE")

    util.create_column(cr, "iot_device", "manufacturer", "varchar")
    util.create_column(cr, "iot_device", "screen_url", "varchar")
    util.create_column(cr, "iot_device", "keyboard_layout", "int4")
    util.create_column(cr, "iot_device", "connected", "boolean")
