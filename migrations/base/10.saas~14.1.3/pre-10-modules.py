# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.merge_module(cr, 'account_tax_cash_basis', 'account')

    util.rename_module(cr, 'base_action_rule', 'base_automation')

    # new modules
    util.new_module(cr, 'base_address_city', deps=('base',))
    util.new_module(cr, 'base_address_extended', deps=('base',))

    # new modules-link
    util.new_module(cr, 'crm_livechat', deps=('crm', 'im_livechat'), auto_install=True)
    util.new_module(cr, 'pos_sale', deps=('point_of_sale', 'sale'), auto_install=True)

    # remove deps
    util.remove_module_deps(cr, 'calendar', ('base_automation',))
    util.remove_module_deps(cr, 'crm', ('base_automation',))
    util.remove_module_deps(cr, 'hr_contract', ('base_automation',))
    util.remove_module_deps(cr, 'hr_timesheet', ('account',))
    util.remove_module_deps(cr, 'sale_crm', ('web_kanban_gauge',))

    # changed deps
    util.remove_module_deps(cr, 'project_issue_sheet', ('hr_timesheet_sheet',))
    util.new_module_dep(cr, 'project_issue_sheet', 'hr_timesheet')

    util.new_module_dep(cr, 'website_portal_sale', 'sale')

    # removed modules
    util.remove_module(cr, 'portal_sale')
    util.remove_module(cr, 'subscription')
    util.remove_module(cr, 'test_workflow')

    if util.has_enterprise():
        # new modules
        util.new_module(cr, 'l10n_mx_edi', deps=('account', 'base_vat', 'base_address_extended'))
        util.new_module(cr, "l10n_mx_edi_cfdi_33", deps={"l10n_mx_edi", "base_address_city"}, auto_install=True)
        util.new_module(cr, "l10n_mx_edi_payment", deps={"l10n_mx_edi_cfdi_33"}, auto_install=True)

        util.new_module(cr, 'mail_github', deps=('mail',))
        util.new_module(cr, 'sale_coupon', deps=('sale',))
        util.new_module(cr, 'web_clearbit', deps=('base_setup', 'web'), auto_install=True)

        # new modules-link
        util.new_module(cr, 'base_automation_hr_contract',
                        deps=('base_automation', 'hr_contract'),
                        auto_install=True)
        util.new_module(cr, 'delivery_barcode', deps=('delivery', 'stock_barcode'),
                        auto_install=True)
        util.new_module(cr, 'l10n_mx_reports', deps=('l10n_mx', 'account_reports'),
                        auto_install=True)

        util.new_module(cr, 'sale_coupon_delivery', deps=('sale_coupon', 'delivery'),
                        auto_install=True)
        util.new_module(cr, 'website_sale_coupon', deps=('website_sale', 'sale_coupon'),
                        auto_install=True)

        # changed deps
        util.new_module_dep(cr, 'helpdesk', 'web_tour')

        util.remove_module_deps(cr, 'account_taxcloud', ('account',))
        util.new_module_dep(cr, 'account_taxcloud', 'l10n_us')

        util.remove_module_deps(cr, 'project_forecast_sale', ('sale_timesheet',))
        util.new_module_dep(cr, 'project_forecast_sale', 'sale')

        # removed modules
        util.remove_module(cr, 'delivery_temando')
        util.remove_module(cr, 'website_portal_followup')
