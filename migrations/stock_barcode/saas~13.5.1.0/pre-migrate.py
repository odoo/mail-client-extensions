# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_company", "keyboard_layout", "varchar", default="qwerty")
    util.create_column(cr, "res_config_settings", "group_barcode_keyboard_shortcuts", "boolean")
