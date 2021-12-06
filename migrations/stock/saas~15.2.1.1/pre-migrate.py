# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    util.rename_xmlid(cr, "stock.access_stock_production_lot", "stock.access_stock_lot")
    util.rename_model(cr, "stock.production.lot", "stock.lot")
