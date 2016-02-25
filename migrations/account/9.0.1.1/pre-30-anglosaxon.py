# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    """
        Anglo-saxon module has been removed and integrated in other modules, thus fix field dependencies
    """

    if util.module_installed(cr, 'account_anglo_saxon'):
        util.move_field_to_module(cr, 'account.invoice.line', 'move_id',
                                  'account_anglo_saxon', 'stock_account')
        util.move_field_to_module(cr, 'product.category',
                                  'property_account_creditor_price_difference_categ',
                                  'account_anglo_saxon', 'purchase')
        util.move_field_to_module(cr, 'product.template',
                                  'property_account_creditor_price_difference',
                                  'account_anglo_saxon', 'purchase')

        util.create_column(cr, 'res_company', 'anglo_saxon_accounting', 'boolean')
        cr.execute("UPDATE res_company SET anglo_saxon_accounting = true")

    # remove module
    util.remove_module(cr, 'account_anglo_saxon')
