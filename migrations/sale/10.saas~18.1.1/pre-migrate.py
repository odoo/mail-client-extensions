# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_field(cr, 'product.template', 'track_service', 'service_type')
    cr.execute(r"""
        UPDATE ir_ui_view
           SET arch_db = regexp_replace(arch_db, '\ytrack_service\y', 'service_type', 'g')
         WHERE id = %s
    """, [util.ref(cr, 'sale.product_template_form_view_invoice_policy')])

    util.rename_field(cr, 'sale.order', 'project_id', 'analytic_account_id')
    util.remove_field(cr, 'sale.order', 'procurement_group_id')

    util.create_column(cr, 'account_invoice_line', 'price_total', 'numeric')
    util.create_column(cr, 'sale_order_line', 'amt_to_invoice', 'numeric')
    util.create_column(cr, 'sale_order_line', 'amt_invoiced', 'numeric')

    util.rename_xmlid(cr, 'sale.orders_followup', 'sale.portal_order_page')

    # cleanup merge from `website_portal_sale`
    payment_views = [
        'crm_team_salesteams_view_kanban_inherit_website_portal_sale',
        'sale_order_view_form',
    ]
    payment_fields = [
        ('crm.team', 'pending_payment_transactions_count'),
        ('crm.team', 'pending_payment_transactions_amount'),
        ('crm.team', 'authorized_payment_transactions_count'),
        ('crm.team', 'authorized_payment_transactions_amount'),
        ('sale.order', 'payment_transaction_count'),
    ]
    if util.module_installed(cr, 'sale_payment'):
        util.env(cr)['ir.config_parameter'].set_param('sale.sale_portal_confirmation_options', 'pay')
        for pv in payment_views:
            util.rename_xmlid(cr, 'sale.' + pv, 'sale_payment.' + pv)
        for pm, pf in payment_fields:
            util.move_field_to_module(cr, pm, pf, 'sale', 'sale_payment')
    else:
        for pv in payment_views:
            util.remove_view(cr, 'sale.' + pv)
        for pm, pf in payment_fields:
            util.remove_field(cr, pm, pf)
