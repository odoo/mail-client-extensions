# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "stock.stock_move_rule")
    util.update_record_from_xml(cr, "stock.stock_move_line_rule")
