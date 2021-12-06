# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "quality.access_stock_production_user", "quality.access_stock_lot_user")
