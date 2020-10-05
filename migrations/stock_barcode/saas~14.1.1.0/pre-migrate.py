# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.company", "keyboard_layout")
    util.remove_field(cr, "res.config.settings", "keyboard_layout")
    util.remove_field(cr, "res.config.settings", "group_barcode_keyboard_shortcuts")

    util.remove_record(cr, "stock_barcode.group_barcode_keyboard_shortcuts")
