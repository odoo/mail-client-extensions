# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_view(cr, 'sale_contract.account_analytic_account_form_form')
    util.remove_view(cr, 'sale_contract.account_analytic_analysis_form_form')
    util.remove_view(cr, 'sale_contract.account_analytic_account_view_form_inherit')
    util.remove_view(cr, 'sale_contract.view_account_analytic_account_template_required')