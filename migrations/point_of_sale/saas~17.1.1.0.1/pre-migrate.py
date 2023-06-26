# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "pos_discount"):
        util.rename_xmlid(cr, "point_of_sale.product_product_consumable", "pos_discount.product_product_consumable")
    else:
        util.delete_unused(cr, "point_of_sale.product_product_consumable")
    util.remove_field(cr, "pos.order", "refunded_order_ids")
    util.remove_field(cr, "pos.order", "refunded_orders_count")
    util.remove_field(cr, "pos.order", "is_refunded")
