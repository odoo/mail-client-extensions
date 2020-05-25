# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, 'stock.stock_warehouse_view_form_editable')
    util.remove_view(cr, 'stock.stock_warehouse_view_tree_editable')

    util.remove_field(cr, 'res.config.settings', 'group_stock_multi_warehouses')
