# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # deleted module
    util.remove_module(cr, 'base_status')

    # new dependance
    util.new_module_dep(cr, 'l10n_be', 'l10n_multilang')
    util.new_module_dep(cr, 'crm_partner_assign', 'portal')
    util.new_module_dep(cr, 'google_base_account', 'base_setup')
