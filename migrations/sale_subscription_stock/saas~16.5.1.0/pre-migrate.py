# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale_subscription_stock.sale_order_portal_content_inherit_subscription")
