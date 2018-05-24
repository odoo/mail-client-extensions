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

    if util.has_enterprise():
        util.new_module(cr, "mail_enterprise", deps={'mail'}, auto_install=True)
        util.new_module(cr, "project_timesheet_forecast",
                        deps={"hr_timesheet", "project_forecast"}, auto_install=True)
        util.new_module(cr, "web_dashboard", deps={"web"})
        util.new_module(cr, "website_sale_dashboard",
                        deps={"website_sale", "web_dashboard"}, auto_install=True)
        util.new_module(cr, "website_sale_dashboard_with_margin",
                        deps={"website_sale", "web_dashboard", "sale_margin"}, auto_install=True)

        util.module_deps_diff(cr, "web_studio", minus={"web_grid", "web_gantt"})

        util.remove_module(cr, "project_forecast_sale")
