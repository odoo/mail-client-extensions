# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("product_expiry.view_stock_quant_tree{_expiry,}"))
    util.rename_xmlid(cr, *eb("product_expiry.view_stock_quant_tree_editable{_expiry,}"))
