# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "sale.subscription", "fiscal_position_id")
    util.remove_field(cr, "sale.subscription.line", "tax_ids")
    cr.execute("DROP TABLE IF EXISTS account_tax_sale_subscription_line_rel")
    util.remove_field(cr, "sale.subscription.line", "price_tax")
    util.remove_field(cr, "sale.subscription.line", "price_total")
    util.remove_field(cr, "sale.subscription.report", "recurring_total_incl")
