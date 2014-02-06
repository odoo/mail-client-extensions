# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    """This migration script is only useful on saas."""
    if util.table_exists(cr, 'payment_provider_account'):
        util.rename_module(cr, 'payment', 'openerp_payment')
        util.rename_model(cr, 'payment.payment', 'openerp_payment.payment')
        util.rename_model(cr, 'payment.provider.account', 'openerp_payment.provider.account')
        util.rename_model(cr, 'payment.creditcard', 'openerp_payment.creditcard')

        util.new_module_dep(cr, 'openerp_enterprise', 'website')
