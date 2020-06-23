# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, xml_id="stock_account.stock_valuation_layer_search")
    util.remove_record(cr, "stock_account.action_stock_inventory_valuation")
