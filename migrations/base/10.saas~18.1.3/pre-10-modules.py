# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_module(cr, 'crm_project')   # artefact that may stay in old databases
    util.rename_module(cr, 'crm_project_issue', 'crm_project')
    util.rename_module(cr, 'website_issue', 'website_form_project')
    util.rename_module(cr, 'website_portal', 'portal')
    util.rename_module(cr, 'website_rating_project_issue', 'website_rating_project')

    util.new_module(cr, 'account_payment', deps={'account', 'payment'})
    util.new_module(cr, 'http_routing', deps={'web'})
    util.new_module(cr, 'transifex', deps={'base'})

    util.new_module_dep(cr, 'account', 'portal')
    util.merge_module(cr, 'website_account', 'account')     # FIXME

    accountant_deps = util.splitlines("""
        account_asset
        account_bank_statement_import
        hr_expense
        l10n_be_intrastat
        l10n_eu_service
        l10n_fr_fec
        test_main_flows
    """)
    for m in accountant_deps:
        util.module_deps_diff(cr, m, plus={'account'}, minus={'account_accountant'})

    util.new_module_dep(cr, 'delivery', 'sale_management')

    # l10n_in
    util.module_deps_diff(cr, 'l10n_in', plus={'account_tax_python'}, minus={'account'})
    util.module_deps_diff(cr, 'l10n_in_schedule6', plus={'account_tax_python'}, minus={'account'})
    util.new_module(cr, 'l10n_in_purchase', deps={'l10n_in', 'purchase'}, auto_install=True)
    util.new_module(cr, 'l10n_in_sale', deps={'l10n_in', 'sale'}, auto_install=True)
    util.new_module(cr, 'l10n_in_stock', deps={'l10n_in', 'stock'}, auto_install=True)

    util.new_module_dep(cr, 'l10n_nl', 'base_address_extended')

    util.merge_module(cr, 'procurement', 'stock')

    util.new_module_dep(cr, 'project', 'portal')
    util.merge_module(cr, 'project_issue', 'project')   # will handle deps

    util.new_module_dep(cr, 'sale', 'portal')
    util.module_deps_diff(cr, 'sale_crm', plus={'sale_management'}, minus={'sale'})
    # Do not undo what have been done in saas~17 as it has to be redo in 11.0
    # saas~18 being a dead release (no one use it), we can keep currently correct dependencies
    # util.module_deps_diff(cr, 'sale_stock', plus={'sale'}, minus={'sale_management'})

    util.module_deps_diff(cr, 'website', plus={'http_routing', 'portal'})

    util.module_deps_diff(cr, 'website_quote', minus={'website_portal_sale'})
    util.module_deps_diff(cr, 'website_rating_project',
                          plus={'website', 'rating_project'},
                          minus={'website_project_issue'})
    util.module_deps_diff(cr, 'website_sale', minus={'website_portal_sale', 'website_account'})
    util.module_deps_diff(cr, 'website_sale_digital', plus={'website_sale'}, minus={'website_portal_sale'})

    util.merge_module(cr, 'website_portal_purchase', 'purchase')
    util.merge_module(cr, 'website_portal_sale', 'sale')
    util.merge_module(cr, 'website_project', 'project')
    util.merge_module(cr, 'website_project_issue', 'project')

    util.new_module(cr, 'website_sale_stock_options',
                    deps={'website_sale_stock', 'website_sale_options'}, auto_install=True)

    if util.has_enterprise():
        util.rename_module(cr, 'marketing_campaign', 'marketing_automation')
    else:
        # you're screw...
        util.remove_module(cr, 'marketing_campaign')
        util.remove_module(cr, 'account_accountant')

    removed_modules = util.splitlines("""
        marketing_campaign_crm_demo

        project_issue_sheet
        website_project_issue_sheet
        rating_project_issue

        stock_calendar  # merge somewhere?
        website_project_timesheet
    """)
    for m in removed_modules:
        util.remove_module(cr, m)
