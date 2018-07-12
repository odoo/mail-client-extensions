# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "stock_fixed_putaway_strat", "product_id", "int4")
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("stock.access_{product_uom_categ,uom_category}_stock_manager"))
    util.rename_xmlid(cr, *eb("stock.access_{product,uom}_uom_stock_manager"))
