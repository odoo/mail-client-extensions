# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mrp_subcontracting.mrp_subcontracting_move_tree_view")
