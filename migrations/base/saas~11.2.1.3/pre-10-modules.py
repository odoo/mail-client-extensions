# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.new_module(cr, "im_support", deps={"mail"})
    util.new_module(cr, "l10n_hk", deps={"account"})
    util.new_module(cr, "social_media", deps={"base"})
    util.force_migration_of_fresh_module(cr, "social_media")

    util.new_module_dep(cr, "iap", "web_settings_dashboard")
    util.new_module_dep(cr, "l10n_cn", "l10n_multilang")
    util.new_module_dep(cr, "mass_mailing", "social_media")
    util.new_module_dep(cr, "website", "social_media")
    util.new_module_dep(cr, "website_quote", "sale_payment")

    util.rename_module(cr, "mrp_repair", "repair")

    if util.has_enterprise():
        util.new_module(cr, "analytic_enterprise", deps={"web_grid", "analytic", "account"}, auto_install=True)
        util.new_module(cr, "l10n_ca_check_printing", deps={"account_check_printing", "l10n_ca"}, auto_install=True)
        util.module_deps_diff(cr, "website_crm_score", minus={"marketing_automation"})
