# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "sale.order.line", "pickup_date")
    util.remove_field(cr, "product.template", "rental_pricing_ids")
    util.remove_field(cr, "product.product", "rental_pricing_ids")
    util.remove_column(cr, "sale_temporal_recurrence", "pricing_id")
