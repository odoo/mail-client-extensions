# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'product.template', 'rules_count')
    util.remove_field(cr, 'product.product', 'rules_count')

    util.remove_view(cr, 'account_analytic_default.product_form_view_default_analytic_button')
    util.remove_view(cr, 'account_analytic_default.product_template_view_default_analytic_button')
