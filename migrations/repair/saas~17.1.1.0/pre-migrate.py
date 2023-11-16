# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "repair.order", "show_set_qty_button")
    util.remove_field(cr, "repair.order", "show_clear_qty_button")
