# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_module(cr, 'base_calendar', 'calendar')
    util.rename_module(cr, 'google_base_account', 'google_account')

    util.new_module_dep(cr, 'calendar', 'web_calendar')
    util.new_module_dep(cr, 'base_action_rule', 'resource')
    util.new_module_dep(cr, 'hr_contract', 'base_action_rule')

    util.remove_module(cr, 'web_shortcuts')
    util.remove_module(cr, 'event_moodle')

    deps = ('hr_recruitment', 'document')
    util.new_module(cr, 'hr_applicant_document', auto_install_deps=deps)

    util.new_module(cr, 'base_geolocalize')
    util.new_module_dep(cr, 'crm_partner_assign', 'base_geolocalize')

    util.new_module_dep(cr, 'auth_signup', 'web')

    # delivery now depend on sale_stock instead of sale and stock
    util.remove_module_deps(cr, 'delivery', ('sale', 'stock', 'purchase'))
    util.new_model_dep(cr, 'delivery', 'sale_stock')

    util.new_module_dep(cr, 'event', 'marketing')

    # website !!
    util.new_module(cr, 'website')
    util.new_module(cr, 'website_mail')

    util.rename_module(cr, 'document_page', 'website_blog')
    util.new_model_dep(cr, 'website_blog', 'website_mail')

    # update module deps to auto isntall website if website_mail is marked to
    # be installed if website_blog is installed (because document_page was)
    util.new_module_dep(cr, 'website_mail', 'website')
    util.new_module_dep(cr, 'website', 'web')
