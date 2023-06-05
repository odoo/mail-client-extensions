# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.change_field_selection_values(cr, "sale.order.alert", "state", {"done": "sale"})
    util.remove_field(cr, "sale.order", "industry_id")
    util.remove_field(cr, "sale.order", "country_id")
    util.remove_field(cr, "sale.order.template", "color")
    util.remove_field(cr, "sale.order.line", "pricing_id")
    util.remove_view(cr, "sale_subscription.sale_order_line_view_tree")
    util.remove_field(cr, "payment.transaction", "renewal_allowed")
