# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "fsm.stock.tracking.line", "wizard_tracking_line_valided", "wizard_tracking_line_validated")
    util.remove_field(cr, "fsm.stock.tracking", "fsm_done")
    util.remove_view(cr, "industry_fsm_stock.stock_product_product_kanban_material")
