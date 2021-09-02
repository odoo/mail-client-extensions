# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.new_module(cr, "account_debit_note", deps={"account"})
    # https://github.com/odoo/odoo/pull/45720
    util.new_module(cr, "l10n_co_pos", deps={"l10n_co", "point_of_sale"}, auto_install=True)
    # https://github.com/odoo/odoo/commit/40bc27774d4eed0a8a23f6762a09c6a10d2af8e8
    util.new_module(cr, "l10n_ch_qriban", deps={"l10n_ch"}, auto_install=True)
    # https://github.com/odoo/odoo/commit/0d8ad9221baebe909aae387498297d403f9ecc0b
    util.new_module(cr, "l10n_dz", deps={"account"})
    # https://github.com/odoo/odoo/pull/65591
    util.new_module(cr, "l10n_it_stock_ddt", deps={"l10n_it_edi", "delivery"}, auto_install=True)
    # https://github.com/odoo/odoo/pull/40776, for `saas~12.3` databases
    util.new_module(cr, "l10n_id", deps={"account", "base_iban", "base_vat"})
    # https://github.com/odoo/odoo/commit/0bf02af0369bca8292abd83b3f8c6434c2c713f3
    util.new_module(cr, "l10n_id_efaktur", deps={"l10n_id"}, auto_install=True)
    # https://github.com/odoo/odoo/pull/46821
    util.new_module(cr, "l10n_fi", deps={"account", "base_iban", "base_vat"})

    # odoo/odoo#40937
    util.new_module(cr, "l10n_se", deps={"account", "base_vat"})
    # odoo/odoo#52034
    util.new_module(cr, "l10n_se_ocr", deps={"l10n_se"}, auto_install=True)

    # odoo/odoo@24b57a377fec77178aad2b433da8f743be9db747
    util.new_module(cr, "odoo_referral", deps={"base", "web"}, auto_install=True)
    util.new_module(cr, "odoo_referral_portal", deps={"website", "odoo_referral"}, auto_install=True)

    util.new_module(cr, "pos_kitchen_printer", deps={"pos_restaurant"}, auto_install=True)

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

        # https://github.com/odoo/enterprise/pull/8496
        util.new_module(cr, "account_reports_cash_basis", deps={"account_reports"})
        # https://github.com/odoo/enterprise/commit/f251bf1152b4f7f0410963469fac34d6470433ee
        util.new_module(cr, "l10n_au_keypay", deps={"l10n_au", "account_accountant"})
        # https://github.com/odoo/enterprise/commit/c460ed12f81e2978e1d37b80ea5f05a674b76a9c
        util.new_module(cr, "l10n_be_sale_intrastat", deps={"sale_intrastat", "l10n_be_intrastat"}, auto_install=True)
        # https://github.com/odoo/enterprise/pull/8999
        util.new_module(cr, "l10n_fi_reports", deps={"l10n_fi", "account_reports"}, auto_install=True)
        # https://github.com/odoo/enterprise/pull/7578
        util.new_module(cr, "account_saft", deps={"account_reports"})
        util.new_module(cr, "l10n_lu_saft", deps={"l10n_lu_reports", "account_saft"}, auto_install=True)
        util.new_module(cr, "l10n_no_saft", deps={"l10n_no", "account_saft"}, auto_install=True)
        # https://github.com/odoo/enterprise/commit/9c6230a68fa63a37015f363335e2a941b3d16258
        util.module_deps_diff(cr, "l10n_mx_edi_landing", plus={"sale_stock"})
        # https://github.com/odoo/enterprise/pull/7967
        util.new_module(cr, "l10n_se_reports", deps={"l10n_se", "account_reports"}, auto_install=True)
        # https://github.com/odoo/enterprise/pull/8767
        util.new_module(cr, "partner_commission", deps={"purchase", "sale_subscription", "website_crm_partner_assign"})

        util.module_deps_diff(
            cr, "pos_blackbox_be", plus={"pos_restaurant_iot", "pos_cash_rounding"}, minus={"pos_restaurant"}
        )
        util.module_auto_install(cr, "module_auto_install", True)

        # https://github.com/odoo/enterprise/pull/6764
        util.module_deps_diff(cr, "hr_contract_salary", plus={"hr_contract_sign"}, minus={"hr"})
        util.force_migration_of_fresh_module(cr, "hr_contract_sign")  # fresh from saas~12.5...

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
