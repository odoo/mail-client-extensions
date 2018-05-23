# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("purchase.access_{product_uom_categ,uom_category}_purchase_manager"))
    util.rename_xmlid(cr, *eb("purchase.access_{product,uom}_uom_purchase_manager"))
