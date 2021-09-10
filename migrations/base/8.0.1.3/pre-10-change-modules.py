# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):

    util.remove_module(cr, 'plugin_outlook')
    util.remove_module(cr, 'plugin_thunderbird')
    util.remove_module(cr, 'plugin')

    util.new_module(cr, 'bus')
    util.rename_module(cr, 'im', 'im_chat')
    util.new_module_dep(cr, 'im_chat', 'bus')
    util.new_module(cr, "im_odoo_support", deps={"im_chat", "web"})

    util.new_module(cr, "payment_authorize", deps={"payment"})
    util.new_module(cr, "payment_sips", deps={"payment"})
    util.rename_module(cr, 'project_mrp', 'sale_service')

    util.new_module_dep(cr, 'l10n_uk', 'account_anglo_saxon')
    util.new_module_dep(cr, 'l10n_us', 'account_anglo_saxon')

    util.remove_module_deps(cr, 'project_issue', ('crm',))
    util.new_module_dep(cr, 'project_issue', 'sales_team')

    util.new_module(cr, 'crm_mass_mailing', deps=('crm', 'mass_mailing'), auto_install=True)

    util.new_module(cr, 'website_instantclick', deps=('website',))
    util.new_module(cr, 'website_sale_options', deps=('website_sale',))

    # new l10n modules
    for cc in 'ae do hu jp no sa sg'.split():
        l10n = 'l10n_' + cc
        util.new_module(cr, l10n, deps=('account', 'account_chart'))

    util.new_module(cr, "l10n_eu_service", deps={"account_accountant"})

    util.new_module(cr, "hw_proxy")
    util.new_module(cr, "hw_screen", deps={"hw_proxy"})
