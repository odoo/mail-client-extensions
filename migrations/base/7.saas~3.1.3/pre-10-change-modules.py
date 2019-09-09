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
    # portal_anonymous is handled in pre-05
    util.remove_module(cr, 'portal_hr_employees')
    util.remove_module(cr, 'portal_crm')
    util.remove_module(cr, 'portal_event')

    deps = ('hr_recruitment', 'document')
    util.new_module(cr, 'hr_applicant_document', deps=deps, auto_install=True)

    util.new_module(cr, 'base_geolocalize', deps=('crm',))
    util.new_module_dep(cr, 'crm_partner_assign', 'base_geolocalize')
    util.force_migration_of_fresh_module(cr, 'base_geolocalize')

    util.new_module_dep(cr, 'auth_signup', 'web')

    # delivery now depend on sale_stock instead of sale and stock
    util.remove_module_deps(cr, 'delivery', ('sale', 'stock', 'purchase'))
    util.new_module_dep(cr, 'delivery', 'sale_stock')

    util.new_module_dep(cr, 'event', 'marketing')

    util.new_module(cr, "gamification", deps={"mail", "email_template", "web_kanban_gauge"})
    util.new_module(cr, "gamification_sale_crm", deps={"gamification", "sale_crm"}, auto_install=True)
    util.new_module(cr, "hr_gamification", deps={"gamification", "hr"}, auto_install=True)

    util.new_module(cr, "payment", deps={"account"}, auto_install=True)
    for provider in {"adyen", "ogone", "paypal", "transfer"}:
        util.new_module(cr, "payment_" + provider, deps={"payment"})

    util.new_module_dep(cr, 'portal_sale', 'payment')
    util.new_module(cr, "product_email_template", deps={"account"})
    util.new_module_dep(cr, "project_timesheet", "procurement")

    # website !!
    util.new_module(cr, 'website', deps={"web", "share", "mail"})
    util.new_module(cr, 'website_mail', deps={"website", "mail"})

    util.rename_module(cr, 'document_page', 'website_blog')
    util.new_module_dep(cr, 'website_blog', 'website_mail')

    util.new_module(cr, "website_partner", deps={"website"})
    util.new_module(cr, "website_google_map", deps={"base_geolocalize", "website_partner", "crm_partner_assign"})
    util.new_module(cr, "website_customer", deps={"website_partner", "website_google_map"})
    util.new_module(cr, "website_crm_partner_assign",
                    deps={"crm_partner_assign", "website_partner", "website_google_map"})
    util.new_module(cr, "website_crm", deps={"website_partner", "crm"})

    util.new_module(cr, "website_event", deps={"website", "website_partner", "website_mail", "event"})
    util.new_module(cr, "website_sale", deps={"website", "sale", "payment"})
    util.new_module(cr, "website_event_sale", deps={"website_event", "event_sale", "website_sale"})
    util.new_module(cr, "website_event_track", deps={"website_event", "website_blog"})
    util.new_module(cr, "website_hr", deps={"website", "hr"})
    util.new_module(cr, "website_hr_recruitment", deps={"website_partner", "hr_recruitment", "website_mail"})
    util.new_module(cr, "website_livechat", deps={"website", "im_livechat"})
    util.new_module(cr, "website_membership",
                    deps={"website_partner", "website_google_map", "association", "website_sale"})
    util.new_module(cr, "website_payment", deps={"website", "payment"})
    util.new_module(cr, "website_project", deps={"website_mail", "project"})
    util.new_module(cr, "website_quote", deps={"website", "sale", "mail"})
    util.new_module(cr, "website_sale_crm", deps={"website_sale", "sale_crm"}, auto_install=True)
    util.new_module(cr, "website_sale_delivery", deps={"website_sale", "delivery"})

    # 'ir.actions.wizard' model is deprecated
    util.delete_model(cr, 'ir.actions.wizard')
