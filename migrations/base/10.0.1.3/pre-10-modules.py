# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if util.has_enterprise():
        util.new_module(cr, 'web_mobile', deps=('web_settings_dashboard',), auto_install=True)
        util.new_module(cr, 'mail_push', deps=('mail', 'web_mobile'), auto_install=True)
        util.new_module(cr, 'stock_barcode_mobile', deps=('stock_barcode', 'web_mobile'),
                        auto_install=True)
        util.new_module(cr, 'hr_expense_sepa', deps=('account_sepa', 'hr_expense'),
                        auto_install=True)
