# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    code = """
       if context.get('active_model') == 'account.payment' and context.get('active_ids'):
           action = env['account.payment'].browse(context['active_ids']).print_checks()
    """
    action = util.ref(cr, 'account_check_printing.action_account_print_checks')
    if action:
        cr.execute("UPDATE ir_act_server SET code=%s WHERE id=%s", [code, action])
