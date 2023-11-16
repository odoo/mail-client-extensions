# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "stock.picking.batch", "show_set_qty_button")
    util.remove_field(cr, "stock.picking.batch", "show_clear_qty_button")
