# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_view(cr, 'account_deferred_revenue.view_product_template_form_inherit')
    util.remove_view(cr, 'account_deferred_revenue.view_account_invoice_asset_form')
    util.remove_view(cr, 'account_deferred_revenue.view_invoice_revenue_recognition_category')
