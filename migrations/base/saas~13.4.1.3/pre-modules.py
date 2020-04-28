# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.new_module_dep(cr, "crm_iap_lead", "partner_autocomplete")
    util.new_module_dep(cr, "crm_iap_lead_enrich", "partner_autocomplete")
    util.remove_module(cr, "odoo_referral_portal")
    util.new_module(cr, "mail_bot_hr", deps={"mail_bot", "hr"}, auto_install=True)
    util.module_deps_diff(cr, "hr", minus={"mail_bot"})
    util.module_deps_diff(cr, "test_mail", minus={"mail_bot"})
    util.new_module_dep(cr, 'l10n_in', 'base_vat')
    util.new_module(cr, "website_project", deps={"website", "project"}, auto_install=True)
    util.force_migration_of_fresh_module(cr, 'website_project')
    # Extracting coupon module from sale_coupon module
    util.new_module(cr, "coupon", deps={"account"})
    util.module_deps_diff(cr, "sale_coupon", plus={"coupon"})
    util.force_migration_of_fresh_module(cr, "coupon", init=True)
    util.merge_module(cr, "account_analytic_default", "account")
    util.merge_module(cr, "account_analytic_default_hr_expense", "hr_expense")
    util.merge_module(cr, "account_analytic_default_purchase", "purchase")

    if util.has_enterprise():
        util.module_deps_diff(cr, "test_mail_enterprise",
                              plus={"marketing_automation_sms"})
        util.module_deps_diff(cr, "test_marketing_automation",
                              plus={"marketing_automation_sms",
                                    "test_mass_mailing",
                                    "test_mail_enterprise",
                                    "test_mail_full"})
