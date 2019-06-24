# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(
        cr, "website_sale_delivery.sale_order_portal_content_inherit_sale_stock_inherit_website_sale_delivery"
    )
