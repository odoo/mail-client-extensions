# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if util.module_installed(cr, 'payment_paypal'):
        return
    cr.execute("SELECT count(*) FROM res_company WHERE paypal_account IS NOT NULL")
    if cr.fetchone()[0]:
        util.force_install_module(cr, 'payment_paypal')
        util.force_migration_of_fresh_module(cr, 'payment_paypal')
