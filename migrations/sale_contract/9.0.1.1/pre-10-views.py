# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    view_list = util.splitlines("""
        account_analytic_account_form_form
        account_analytic_analysis_form_form
        account_analytic_account_view_form_inherit
        view_account_analytic_account_template_required
        view_account_analytic_account_overdue_search
        view_account_analytic_account_tree_c2c_3
    """)
    for view in view_list:
        util.remove_view(cr, "sale_contract." + view)
