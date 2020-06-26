# -*- coding: utf-8 -*-

from odoo.upgrade import util

def migrate(cr, version):
    util.remove_view(cr, "iot.view_add_iot_box_inherit_pairing")
    util.create_column(cr, "add_iot_box", "pairing_code", "varchar")
