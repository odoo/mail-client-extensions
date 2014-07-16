# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    util.new_module(cr, 'bus')
    util.rename_module(cr, 'im', 'im_chat')
    util.new_module_dep(cr, 'im_chat', ('bus',))

    util.rename_module(cr, 'project_mrp', 'sale_service')

    util.new_module_dep(cr, 'l10n_us', ('account_anglo_saxon',))
