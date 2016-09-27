# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.drop_workflow(cr, 'account.invoice')

    util.rename_model(cr, 'account.operation.template', 'account.reconcile.model')

    renames = util.splitlines("""
        account.%s_comp_rule
        account.access_%s
        account.view_%s_form
        account.view_%s_tree
        account.view_%s_search
        account.action_%s
    """)

    for pattern in renames:
        util.rename_xmlid(cr, pattern % 'account_operation_template', pattern % 'account_reconcile_model')
