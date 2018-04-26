# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.merge_module(cr, 'account_cash_basis_base_account', 'account', tolerant=True)
    util.rename_module(cr, 'product_extended', 'mrp_bom_cost')

    util.new_module(cr, 'uom', deps={'base'})

    util.new_module_dep(cr, 'hr_timesheet', 'analytic')
    util.new_module_dep(cr, 'l10n_lu', 'l10n_multilang')
    util.new_module_dep(cr, 'product', 'uom')
    util.force_migration_of_fresh_module(cr, 'uom')
    util.remove_module_deps(cr, 'project', {'analytic'})

    util.module_deps_diff(cr, 'survey', plus={'http_routing'}, minus={'website'})
    util.new_module(cr, 'website_survey', deps={'website', 'survey'},
                    auto_install=util.module_installed(cr, 'survey'))
