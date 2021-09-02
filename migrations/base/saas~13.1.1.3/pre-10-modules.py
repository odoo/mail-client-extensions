# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.new_module(cr, "fleet_account", deps={"fleet", "account"})
    util.new_module(cr, "mrp_product_expiry", deps={"mrp", "product_expiry"}, auto_install=True)
    util.new_module(cr, "test_base_automation", deps={"base_automation"})

    util.module_deps_diff(cr, "im_livechat", plus={"digest"})
    util.module_deps_diff(cr, "l10n_it_edi", plus={"fetchmail"})

    util.rename_module(cr, "website_rating", "portal_rating")
    util.module_deps_diff(cr, "portal_rating", plus={"portal"}, minus={"website_mail"})

    util.module_deps_diff(cr, "test_mail_full", plus={"test_mass_mailing"})

    util.merge_module(cr, "pos_cash_rounding", "point_of_sale")
    util.merge_module(cr, "website_theme_install", "website")

    if util.has_enterprise():
        util.new_module(
            cr,
            "account_accountant_check_printing",
            deps={"account_accountant", "account_check_printing"},
            auto_install=True,
        )

        util.new_module(cr, "approvals_purchase", deps={"approvals", "purchase"}, auto_install=True)
        util.new_module(
            cr,
            "approvals_purchase_stock",
            deps={"approvals_purchase", "purchase_stock"},
            auto_install=True,
        )
        util.new_module(cr, "delivery_iot", deps={"delivery", "iot"}, auto_install=True)
        util.new_module(cr, "fleet_dashboard", deps={"fleet", "web_dashboard"}, auto_install=True)

        util.new_module(cr, "hr_work_entry_contract", deps={"hr_work_entry", "hr_contract"})
        util.new_module(
            cr,
            "hr_recruitment_reports",
            deps={"hr_recruitment", "web_dashboard"},
            auto_install=True,
        )

        util.new_module(
            cr,
            "industry_fsm_sale",
            deps={"industry_fsm", "sale_timesheet_enterprise"},
            auto_install=True,
        )
        util.new_module(
            cr,
            "industry_fsm_sale_report",
            deps={"industry_fsm_sale", "industry_fsm_report"},
            auto_install=True,
        )
        util.new_module(cr, "mrp_workorder_expiry", deps={"mrp_workorder", "product_expiry"}, auto_install=True)
        util.new_module(cr, "sale_account_accountant", deps={"sale", "account_accountant"}, auto_install=True)

        util.new_module(
            cr,
            "social_demo",
            deps={"social", "social_facebook", "social_twitter", "social_linkedin", "product"},
        )
        util.new_module(cr, "stock_accountant", deps={"stock_account", "account_accountant"}, auto_install=True)
        util.new_module(
            cr,
            "stock_barcode_mrp_subcontracting",
            deps={"stock_barcode", "mrp_subcontracting"},
            auto_install=True,
        )
        util.new_module(cr, "test_web_grid", deps={"web_grid"})

        util.module_deps_diff(cr, "account_bank_statement_import", plus={"account_accountant"}, minus={"account"})
        util.module_deps_diff(cr, "account_batch_payment", plus={"account_accountant"}, minus={"account"})
        util.module_deps_diff(cr, "account_sepa_direct_debit", plus={"account_accountant"})

        util.module_deps_diff(cr, "approvals", plus={"product"})

        util.module_deps_diff(
            cr,
            "hr_payroll",
            plus={"hr_work_entry_contract"},
            minus={"hr_contract", "hr_holidays", "hr_work_entry"},
        )
        util.force_migration_of_fresh_module(cr, "hr_work_entry_contract")
        util.new_module(
            cr,
            "hr_work_entry_holidays",
            deps={"hr_work_entry_contract", "hr_holidays"},
            auto_install=True,
        )
        util.force_migration_of_fresh_module(cr, "hr_work_entry_holidays")
        util.new_module(
            cr,
            "hr_payroll_holidays",
            deps={"hr_payroll", "hr_work_entry_holidays"},
            auto_install=True,
        )

        util.module_deps_diff(cr, "hr_referral", plus={"hr_recruitment_reports"})
        util.module_deps_diff(cr, "industry_fsm", plus={"timesheet_grid"}, minus={"sale_timesheet_enterprise"})
        util.module_deps_diff(cr, "industry_fsm_report", minus={"project"})
        util.module_deps_diff(cr, "industry_fsm_stock", plus={"industry_fsm_sale"}, minus={"industry_fsm"})

        util.module_deps_diff(cr, "l10n_be_hr_payroll", plus={"hr_work_entry_holidays"})

        util.rename_module(cr, "ocn_client", "mail_mobile")
        util.module_deps_diff(cr, "mail_mobile", plus={"mail_enterprise", "base_setup"}, minus={"mail"})

        util.module_deps_diff(cr, "web_mobile", plus={"web_enterprise"}, minus={"base_setup"})

    else:
        util.remove_module(cr, "account_bank_statement_import")

    util.remove_module(cr, "l10n_cn_standard")
    util.remove_module(cr, "web_diagram")
