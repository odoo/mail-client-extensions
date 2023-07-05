# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "stock.move", "display_clear_serial")
    util.remove_model(cr, "stock.import.lot")
    util.remove_model(cr, "stock.generate.serial")
    util.remove_field(cr, "stock.inventory.adjustment.name", "show_info")
