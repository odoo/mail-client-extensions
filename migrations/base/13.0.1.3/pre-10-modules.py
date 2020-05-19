# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.new_module(cr, "l10n_il", deps={"account"})
    util.new_module(cr, "l10n_lt", deps={"l10n_multilang"})
    util.new_module(cr, "l10n_dk", deps={"account", "base_iban", "base_vat"})
    util.new_module(cr, "odoo_referral", deps={"base", "web"}, auto_install=True)
    util.new_module(cr, "odoo_referral_portal", deps={"website", "odoo_referral"}, auto_install=True)
    util.new_module(cr, "hr_holidays_calendar", deps={"hr_holidays", "calendar"}, auto_install=True)
    if util.has_enterprise():
        util.new_module(cr, "pos_hr_l10n_be", deps={"pos_hr", "pos_blackbox_be"}, auto_install=True)
        util.module_deps_diff(cr, "pos_blackbox_be", plus={"pos_iot"})
        util.module_deps_diff(cr, "crm_enterprise", plus={"web_map"})
        util.merge_module(cr, "l10n_mx_edi_payment", "l10n_mx_edi")
        util.merge_module(cr, "account_reports_cash_flow", "account_reports")
        util.new_module(cr, "hr_holidays_gantt_calendar", deps={"hr_holidays_calendar", "web_gantt"}, auto_install=True)

        util.new_module(
            cr, "social_linkedin_company_support", deps={"social_linkedin"}, auto_install=True
        )
