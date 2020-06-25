# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    util.remove_field(cr, "res.config.settings", "group_stock_multi_warehouses")

    util.rename_xmlid(cr, *eb("stock.action_orderpoint{_form,}"))
    util.remove_record(cr, "stock.product_open_orderpoint")
    util.remove_record(cr, "stock.product_open_orderpoint")

    util.remove_view(cr, "stock.stock_warehouse_view_form_editable")
    util.remove_view(cr, "stock.stock_warehouse_view_tree_editable")
    util.remove_view(cr, "stock.view_warehouse_orderpoint_tree")
