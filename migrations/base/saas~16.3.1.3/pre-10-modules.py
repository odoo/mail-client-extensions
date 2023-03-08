# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "web_kanban_gauge", "web")
    util.merge_module(cr, "pos_epson_printer_restaurant", "pos_epson_printer")
    if util.has_enterprise():
        util.merge_module(cr, "pos_restaurant_iot", "pos_iot")
