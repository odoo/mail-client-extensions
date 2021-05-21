# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.new_module(cr, "iap", deps={"web"}, auto_install=True)

    if not util.has_enterprise():
        # moved from enterprise \o/
        util.new_module(cr, "sms", deps={"iap", "mail"}, auto_install=True)
        util.new_module(cr, "calendar_sms", deps={"calendar", "sms"}, auto_install=True)
    else:
        util.new_module_dep(cr, "account_accountant", "account_reports")
        util.new_module_dep(cr, "sms", "iap")
        util.remove_module(cr, "sms_fortytwo")

        util.new_module(
            cr,
            "website_sale_taxcloud_delivery",
            deps=("website_sale_delivery", "website_sale_account_taxcloud"),
            auto_install=True,
        )
        util.new_module(cr, "l10n_uk_reports_hmrc", deps={"l10n_uk_reports"}, auto_install=True)

        # https://github.com/odoo/enterprise/pull/6291
        util.new_module(cr, "account_reports_cash_flow", deps={"account_reports"}, auto_install=True)

    # Somehow, this is possible to have the default or bootswatch theme installed in addition to one other theme
    # if you come from Odoo 9.0 or Odoo 10.0, but Odoo 11.0 doesn't support it.
    if util.module_installed(cr, "website"):
        cr.execute(
            """
                SELECT name
                FROM ir_module_module
                WHERE name like 'theme_%%'
                AND state in %s
            """,
            (util._INSTALLED_MODULE_STATES,),
        )
        installed_themes = [t[0] for t in cr.fetchall()]
        for theme in ["theme_default", "theme_bootswatch"]:
            if len(installed_themes) > 1 and theme in installed_themes:
                util.uninstall_module(cr, theme)
                installed_themes.remove(theme)
