# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    util.remove_column(cr, "sale_order", "old_subscription_id")
    util.remove_column(cr, "sale_order_line", "old_subscription_line_id")
    util.remove_column(cr, "sale_order_line", "old_subscription_id")
    util.remove_column(cr, "sale_order_template", "old_template_id")
    util.remove_column(cr, "account_analytic_tag_sale_order_rel", "sale_subscription_id")
    util.remove_column(cr, "sale_order_starred_user_rel", "old_subscription_id")
    util.remove_column(cr, "sale_order_template_tag_rel", "old_template_id")

    util.remove_view(cr, "sale_subscription.sale_subscription_view_list")
    util.remove_view(cr, "sale_subscription.sale_subscription_view_form")
    util.remove_view(cr, "sale_subscription.sale_subscription_view_pivot")
    util.remove_view(cr, "sale_subscription.sale_subscription_view_graph")
    util.remove_view(cr, "sale_subscription.sale_subscription_view_cohort")
