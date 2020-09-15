# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, xml_id="mrp_mps.mrp_mps_stock_move_tree_view")
