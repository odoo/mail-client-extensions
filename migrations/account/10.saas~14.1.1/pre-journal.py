# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if util.module_installed(cr, 'payment_transfer'):
        util.move_field_to_module(cr, 'account.journal', 'display_on_footer',
                                  'account', 'payment_transfer')
        util.rename_field(cr, 'account.journal', 'display_on_footer', 'use_in_payment')
    else:
        util.remove_field(cr, 'account.journal', 'display_on_footer')
