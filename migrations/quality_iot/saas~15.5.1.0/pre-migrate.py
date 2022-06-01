# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "quality.check", "ip", "quality_control_iot", "quality_iot")
    util.move_field_to_module(cr, "quality.check", "device_name", "quality_control_iot", "quality_iot")
    util.move_field_to_module(cr, "quality.check", "identifier", "quality_control_iot", "quality_iot")
