# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    if util.has_enterprise():
        pass

    util.rename_xmlid(cr,
                      'account_tax_adjustments.menu_action_account_form',
                      'account.menu_action_tax_adjustment')     # will avoid duplicated xmild
    util.merge_module(cr, 'account_tax_adjustments', 'account')

    util.new_module(cr, 'contacts', deps=('base',))

    if util.module_installed(cr, 'crm_partner_assign'):
        util.force_install_module(cr, 'website_crm_partner_assign')
    util.remove_module_deps(cr, 'website_google_map', ('crm_partner_assign',))
    util.merge_module(cr, 'crm_partner_assign', 'website_crm_partner_assign')
    for newdep in ('base_geolocalize', 'crm', 'account', 'portal', 'website_portal'):
        util.new_module_dep(cr, 'website_crm_partner_assign', newdep)
    util.new_module_dep(cr, 'website_customer', 'website_crm_partner_assign')  # not already done?

    util.rename_module(cr, 'hr_equipment', 'maintenance')
    util.remove_module_deps(cr, 'maintenance', ('hr',))
    util.new_module_dep(cr, 'maintenance', 'mail')
    util.new_module(cr, 'hr_maintenance', deps=('hr', 'maintenance'), auto_install=True)

    # >>> mrp
    util.remove_module_deps(cr, 'mrp', ('procurement', 'stock_account', 'report'))
    util.new_module_dep(cr, 'mrp', 'stock')
    util.new_module(cr, 'purchase_mrp', deps=('purchase', 'mrp'), auto_install=True)
    util.merge_module(cr, 'mrp_operations', 'mrp')       # FIXME confirm with jco
    # <<<

    util.remove_module_deps(cr, 'product_extended', ('product', 'purchase', 'sale'))    # Wut?

    util.remove_module_deps(cr, 'product_visible_discount', ('purchase',))

    util.remove_module_deps(cr, 'project', ('portal',))
    util.remove_module_deps(cr, 'project_issue', ('sales_team',))

    util.new_module(cr, 'sale_service_rating', deps=('sale_timesheet', 'rating_project'),
                    auto_install=True)

    util.new_module_dep(cr, 'subscription', 'sales_team')

    util.new_module(cr, 'web_tour', deps=('web',), auto_install=True)
    for mod in 'account_accountant crm hr_expense hr_recruitment mail sale'.split():
        util.new_module_dep(cr, mod, 'web_tour')

    util.remove_module_deps(cr, 'website_portal_sale', ('sale',))
    util.new_module_dep(cr, 'website_portal_sale', 'portal_sale')

    util.new_module(cr, 'website_project', deps=('website_portal', 'project'), auto_install=True)
    util.new_module_dep(cr, 'website_project_issue', 'website_project')
    util.remove_module_deps(cr, 'website_project_issue', ('website_portal',))
    util.new_module(cr, 'website_project_timesheet', deps=('website_project', 'hr_timesheet'),
                    auto_install=True)

    util.new_module_dep(cr, 'website_sale', 'website_form')

    # cleaning
    to_remove = util.splitlines("""
        product_uos
        web_tip
        mail_tip
        web_analytics
    """)
    for mod in to_remove:
        util.remove_module(cr, mod)
