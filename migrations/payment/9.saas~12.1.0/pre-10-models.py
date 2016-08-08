# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("UPDATE payment_acquirer SET auto_confirm = 'confirm_so' WHERE auto_confirm != 'none'")
    util.rename_model(cr, 'payment.method', 'payment.token')
    util.rename_field(cr, 'payment.transaction', 'payment_method_id', 'payment_token_id')

    util.rename_field(cr, 'res.partner', 'payment_method_ids', 'payment_token_ids')
    util.rename_field(cr, 'res.partner', 'payment_method_count', 'payment_token_count')

    renames = util.splitlines("""
        user_rule
        tree_view
        view_search
        view_form
        action
        menu
    """)
    for r in renames:
        util.rename_xmlid(cr, 'payment.payment_method_' + r, 'payment.payment_token_' + r)
