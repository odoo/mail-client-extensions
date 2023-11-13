# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "stock.picking.type", "show_reserved")
    util.remove_field(cr, "stock.picking", "show_reserved")
    util.remove_field(cr, "stock.move", "show_reserved")
