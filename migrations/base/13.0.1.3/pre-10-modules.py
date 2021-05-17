# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.new_module(cr, "account_debit_note", deps={"account"})
    util.new_module(cr, "l10n_il", deps={"account"})
    util.new_module(cr, "l10n_lt", deps={"l10n_multilang"})
    util.new_module(cr, "l10n_dk", deps={"account", "base_iban", "base_vat"})

    # odoo/odoo#40937
    util.new_module(cr, "l10n_se", deps={"account", "base_vat"})
    # odoo/odoo#52034
    util.new_module(cr, "l10n_se_ocr", deps={"l10n_se"}, auto_install=True)

    # odoo/odoo@24b57a377fec77178aad2b433da8f743be9db747
    util.new_module(cr, "odoo_referral", deps={"base", "web"}, auto_install=True)
    util.new_module(cr, "odoo_referral_portal", deps={"website", "odoo_referral"}, auto_install=True)

    util.new_module(cr, "hr_holidays_calendar", deps={"hr_holidays", "calendar"}, auto_install=True)

    # odoo/odoo@3d43e65b4333c5491375f49feffbd1370b2ab4f9
    util.new_module(cr, "pos_six", deps={"point_of_sale"})

    if util.has_enterprise():
        util.new_module(cr, "l10n_ar_edi", deps={"account_debit_note", "l10n_ar"}, auto_install=True)
        util.new_module(cr, "l10n_cl_edi", deps={"account_debit_note", "l10n_cl"}, auto_install=True)
        util.new_module(cr, "l10n_lu_reports_electronic", deps={"l10n_lu_reports"}, auto_install=True)
        util.new_module(
            cr,
            "l10n_lu_reports_electronic_xml_2_0",
            deps={"l10n_lu_reports_electronic", "account_asset"},
            auto_install=True,
        )
        util.new_module(
            cr, "l10n_nl_report_intrastat", deps={"l10n_nl_reports", "account_intrastat"}, auto_install=True
        )
        util.new_module(cr, "pos_hr_l10n_be", deps={"pos_hr", "pos_blackbox_be"}, auto_install=True)
        util.module_deps_diff(cr, "pos_blackbox_be", plus={"pos_iot"})
        util.module_deps_diff(cr, "crm_enterprise", plus={"web_map"})
        util.merge_module(cr, "l10n_mx_edi_payment", "l10n_mx_edi")
        util.merge_module(cr, "account_reports_cash_flow", "account_reports")
        util.new_module(cr, "hr_holidays_gantt_calendar", deps={"hr_holidays_calendar", "web_gantt"}, auto_install=True)

        util.new_module(cr, "social_linkedin_company_support", deps={"social_linkedin"}, auto_install=True)
        util.new_module(cr, "sale_amazon_authentication", deps={"sale_amazon"}, auto_install=True)
        util.new_module(
            cr, "sale_subscription_timesheet", deps={"sale_subscription", "sale_timesheet"}, auto_install=True
        )

        util.new_module(cr, "l10n_de_pos_cert", deps={"l10n_de", "point_of_sale", "iap"}, auto_install=True)
        util.new_module(cr, "l10n_de_pos_res_cert", deps={"pos_restaurant", "l10n_de_pos_cert"}, auto_install=True)

    if util.has_design_themes():
        util.new_module(
            cr,
            "test_themes",
            deps={
                # CE themes
                "theme_bootswatch",
                "theme_default",
                # design-themes themes
                "theme_anelusia",
                "theme_artists",
                "theme_avantgarde",
                "theme_beauty",
                "theme_bewise",
                "theme_bistro",
                "theme_bookstore",
                "theme_clean",
                "theme_enark",
                "theme_graphene",
                "theme_kea",
                "theme_kiddo",
                "theme_loftspace",
                "theme_monglia",
                "theme_nano",
                "theme_notes",
                "theme_odoo_experts",
                "theme_orchid",
                "theme_real_estate",
                "theme_treehouse",
                "theme_vehicle",
                "theme_yes",
                "theme_zap",
            },
        )
