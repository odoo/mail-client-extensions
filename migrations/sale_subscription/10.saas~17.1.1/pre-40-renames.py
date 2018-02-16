# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    renames = util.splitlines("""
        sale_subscription.module_category_{contract,subscription}_management
        sale_subscription.group_sale_{contract,subscription}_view
        sale_subscription.group_sale_{contract,subscription}_manager

        sale_subscription.sale_{contract,subscription}_report_personal_rule

        sale_subscription.account_analytic_account_view_inherit_sale_{contract,subscription}
        sale_subscription.product_template_search_view_inherit_sale_{contract,subscription}
        sale_subscription.res_partner_view_inherit_sale_{contract,subscription}

        {website_contract,sale_subscription}.sale_order_view_tree_subscription
        {website_contract,sale_subscription}.wizard_form_view
        {website_contract,sale_subscription}.wizard_action
        {website_contract,sale_subscription}.sale_subscription_action_filtered
        {website_contract,sale_subscription}.sale_subscription_template_view_kanban
        {website_contract,sale_subscription}.sale_subscription_view_kanban

    """)
    for r in renames:
        util.rename_xmlid(cr, *util.expand_braces(r))

    # some cleanup
    util.remove_view(cr, 'sale_subscription.sale_order_view_form_subscription')
