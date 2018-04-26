# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'sale.order.line', 'amt_to_invoice')
    util.remove_field(cr, 'sale.order.line', 'amt_invoiced')
    util.remove_view(cr, 'sale.product_template_form_view_invoice_policy')

    util.rename_field(cr, 'sale.report', 'amt_to_invoice', 'amount_to_invoice')
    util.rename_field(cr, 'sale.report', 'amt_invoiced', 'amount_invoiced')

    cr.execute("""
        UPDATE ir_act_window
           SET binding_model_id = NULL
         WHERE id=%s
    """, [util.ref(cr, 'sale.action_view_sale_advance_payment_inv')])
