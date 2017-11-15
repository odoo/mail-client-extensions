# -*- coding: utf-8 -*-
from functools import partial
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version, module='website_subscription'):
    fqn = partial('{}.{}'.format, module)

    renames = util.splitlines("""
        email_%s_open
        %s_portal
        %s_public

        %s      # main template

        portal_my_home_menu_%s
        portal_my_home_%s
        portal_my_%ss   # beware trailing `s`

        email_%s_open
    """)
    for x in renames:
        x = fqn(x)
        util.rename_xmlid(cr, x % 'contract', x % 'subscription')
        util.force_noupdate(cr, x % 'subscription', False)

    old_views = util.splitlines("""
        assets_backend
        chatter_chagne_contract
        chatter_add_option
        chatter_remove_option
        chatter_add_paid_option
        prepaid
        modal_remove
        modal_add
        change_template
        preview_template
        template_panel
        so_quotation

        view_sale_quote_template_form
        sale_order_form_quote_inherit_website_contract
        sale_subscription_view_form_inherit_sale_contract
        sale_subscription_template_view_form_inherit_sale_contract
    """)
    for v in old_views:
        util.remove_view(cr, fqn(v))

    if util.module_installed(cr, 'website_quote_subscription'):
        util.rename_xmlid(cr, fqn('contract_pricing'),
                          'website_quote_subscription.subscription_pricing')
        util.force_noupdate(cr, 'website_quote_subscription.subscription_pricing')
        util.rename_xmlid(cr, fqn('order_line_row'),
                          'website_quote_subscription.order_line_row')
        util.force_noupdate(cr, 'website_quote_subscription.order_line_row')
    else:
        util.remove_view(cr, fqn('contract_pricing'))
        util.remove_view(cr, fqn('order_line_row'))

    util.remove_field(cr, 'sale.order', 'contract_template')
    util.remove_field(cr, 'sale.order.line', 'force_price')
    util.remove_field(cr, 'sale.quote.template', 'contract_template')

    for l in 'mandatory option inactive custom'.split():
        util.remove_field(cr, 'sale.subscription', 'recurring_%s_lines' % l)

    for f in 'plan_description user_selectable subscription_template_option_ids partial_invoice website_url'.split():
        util.remove_field(cr, 'sale.subscription.template', f)
