# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.new_module(cr, "adyen_platforms", deps={"mail", "web"})
    util.new_module(cr, "payment_odoo_by_adyen", deps={"payment", "adyen_platforms"})
    util.module_deps_diff(cr, "pos_adyen", plus={"adyen_platforms"})
    util.new_module(cr, "payment_fix_register_token", deps={"payment"}, auto_install=True)

    # deps chamged by odoo/odoo@59d16513a019d52dd090e09c09be4675aa868baf (odoo/odoo#62730)
    util.module_deps_diff(cr, "l10n_be_edi", plus={"account_edi_ubl"}, minus={"account_edi"})

    # https://github.com/odoo/odoo/pull/62900
    util.new_module(cr, "sale_timesheet_edit", deps={"sale_timesheet"}, auto_install=True)

    # https://github.com/odoo/odoo/pull/63337
    util.new_module(cr, "account_edi_extended", deps={"account_edi"}, auto_install=False)

    # https://github.com/odoo/odoo/pull/67923
    util.new_module(cr, "account_edi_proxy_client", deps={"account_edi"}, auto_install=False)
    util.new_module(
        cr,
        "l10n_it_edi_sdicoop",
        deps={"l10n_it_edi", "account_edi_extended", "account_edi_proxy_client"},
        auto_install=False,
    )

    if util.has_enterprise():
        util.new_module(cr, "account_reports_tax", deps={"account_reports"}, auto_install=True)

        # https://github.com/odoo/enterprise/pull/14895
        util.new_module(cr, "account_online_synchronization", deps={"account_online_sync"}, auto_install=True)

        # https://github.com/odoo/enterprise/pull/15264
        util.new_module(
            cr,
            "helpdesk_sale_timesheet_edit",
            deps={"helpdesk_sale_timesheet", "sale_timesheet_edit"},
            auto_install=True,
        )

        # https://github.com/odoo/enterprise/pull/15364
        util.new_module(cr, "l10n_be_hr_payroll_273S_274", deps={"l10n_be_hr_payroll"}, auto_install=True)
        util.new_module(
            cr,
            "documents_l10n_be_hr_payroll_273S_274",
            deps={"l10n_be_hr_payroll_273S_274", "documents_l10n_be_hr_payroll"},
            auto_install=True,
        )
        util.new_module(
            cr,
            "l10n_be_hr_payroll_273S_274_account",
            deps={"l10n_be_hr_payroll_account", "l10n_be_hr_payroll_273S_274"},
            auto_install=True,
        )

        # https://github.com/odoo/enterprise/pull/15297
        util.new_module(
            cr,
            "l10n_pe_edi",
            deps={
                "iap",
                "l10n_pe",
                "l10n_latam_invoice_document",
                "product_unspsc",
                "account_debit_note",
                "account_edi_extended",
            },
            auto_install=False,
        )

        # https://github.com/odoo/enterprise/pull/14938
        util.new_module(cr, "pos_l10n_se", deps={"pos_restaurant", "pos_iot", "l10n_se"})

        # https://github.com/odoo/enterprise/pull/19638
        util.module_deps_diff(cr, "helpdesk", plus={"web_cohort"})

    util.remove_module(cr, "website_gengo")
    util.remove_module(cr, "base_gengo")
