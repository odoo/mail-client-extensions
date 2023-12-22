# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "stock.quant", "priority")
    util.rename_xmlid(cr, "stock.stock_location_inter_wh", "stock.stock_location_inter_company")
