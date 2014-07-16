# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    util.new_module(cr, 'bus')
    util.rename_module(cr, 'im', 'im_chat')
    util.new_module_dep(cr, 'im_chat', 'bus')

    util.rename_module(cr, 'project_mrp', 'sale_service')

    util.new_module_dep(cr, 'l10n_uk', 'account_anglo_saxon')
    util.new_module_dep(cr, 'l10n_us', 'account_anglo_saxon')

    util.remove_module_deps(cr, 'project_issue', ('crm',))
    util.new_module_dep(cr, 'project_issue', 'sales_team')

    util.new_module(cr, 'crm_mass_mailing', auto_install_deps=('crm', 'mass_mailing'))

    util.new_module(cr, 'website_instantclick')
    util.new_module(cr, 'website_sale_options')

    # new l10n modules
    for cc in 'ae hu sg'.split():
        l10n = 'l10n_' + cc
        util.new_module(cr, l10n)
        util.new_module_dep(cr, l10n, 'account')
        util.new_module_dep(cr, l10n, 'account_chart')
