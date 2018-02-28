# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb('{website_sale_stock,sale_stock}.portal_order_page_shipping'),
                      noupdate=False)
