# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "quality_check", "finished_lot_id")
    util.remove_view(cr, "mrp_workorder.mrp_production_view_search_inherit_planning")
