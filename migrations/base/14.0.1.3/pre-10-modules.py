from odoo.upgrade import util


def migrate(cr, version):
    util.new_module(cr, "adyen_platforms", deps={"mail", "web"})
    util.new_module(cr, "payment_odoo_by_adyen", deps={"payment", "adyen_platforms"})
    util.module_deps_diff(cr, "pos_adyen", plus={"adyen_platforms"})
    util.new_module(cr, "payment_fix_register_token", deps={"payment"}, auto_install=True)

    # https://github.com/odoo/odoo/commit/e23b9bfd47b2a8aee4468fdd3f35aced81761eb3
    util.new_module(cr, "l10n_ar_website_sale", deps={"l10n_ar", "website_sale"}, auto_install=True)
    # deps chamged by odoo/odoo@59d16513a019d52dd090e09c09be4675aa868baf (odoo/odoo#62730)
    util.module_deps_diff(cr, "l10n_be_edi", plus={"account_edi_ubl"}, minus={"account_edi"})
    # https://github.com/odoo/odoo/pull/107084
    util.module_deps_diff(cr, "l10n_dz", plus={"l10n_multilang"})
    # https://github.com/odoo/odoo/commit/e4f95688fe8786ae898c7180b263a4176a0537b4
    util.new_module(cr, "l10n_cz", deps={"account", "base_iban", "base_vat"})
    # https://github.com/odoo/odoo/commit/234fd4c1a4c6d11ecc329552f9e828bd6047f674
    util.new_module(cr, "l10n_de_purchase", deps={"l10n_de", "purchase"}, auto_install=True)
    util.new_module(cr, "l10n_de_repair", deps={"l10n_de", "repair"}, auto_install=True)
    util.new_module(cr, "l10n_de_sale", deps={"l10n_de", "sale"}, auto_install=True)
    util.new_module(cr, "l10n_de_stock", deps={"l10n_de", "stock"}, auto_install=True)

    # https://github.com/odoo/odoo/commit/eb41f0de553906e09d199190544c878a9d1a7e85
    util.new_module(cr, "l10n_sk", deps={"account", "base_iban", "base_vat"})

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

    # https://github.com/odoo/odoo/pull/70302
    util.new_module(cr, "l10n_es_edi_sii", deps={"l10n_es", "account_edi_extended"})

    # https://github.com/odoo/odoo/pull/104891
    util.new_module(cr, "sale_mrp_margin", deps={"sale_mrp", "sale_stock_margin"}, auto_install=True)

    # https://github.com/odoo/odoo/pull/127221
    util.module_deps_diff(cr, "mass_mailing_event_sms", plus={"mass_mailing_event"})

    # https://github.com/odoo/odoo/pull/83849
    util.new_module(cr, "account_edi_ubl_cii", deps={"account_edi"})
    util.new_module(
        cr,
        "l10n_account_edi_ubl_cii_tests",
        deps={
            "l10n_generic_coa",
            "account_edi_ubl_cii",
            "l10n_fr",
            "l10n_be",
            "l10n_de",
        },
    )

    # https://github.com/odoo/odoo/pull/114822
    util.new_module(cr, "l10n_lu_peppol_id", deps={"l10n_lu", "account_edi_ubl_cii"})

    # https://github.com/odoo/odoo/pull/79829
    util.new_module(cr, "l10n_gcc_invoice", deps={"account"})
    util.new_module(cr, "l10n_sa_invoice", deps={"l10n_sa", "l10n_gcc_invoice"})

    # https://github.com/odoo/odoo/pull/80214
    util.new_module(cr, "l10n_gcc_pos", deps={"point_of_sale", "l10n_gcc_invoice"}, auto_install=True)

    # https://github.com/odoo/odoo/pull/81280
    util.new_module(cr, "l10n_ph", deps={"account", "base_vat", "l10n_multilang"})

    # https://github.com/odoo/odoo/pull/92954
    util.new_module(cr, "l10n_fr_facturx_chorus_pro", deps={"account", "account_edi_facturx", "l10n_fr"})

    if util.has_enterprise():
        util.new_module(cr, "account_reports_tax", deps={"account_reports"}, auto_install=True)

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
        # https://github.com/odoo/enterprise/commit/6d44bda491d750e58f6218df048913cec16bdeda
        util.new_module(cr, "l10n_be_hr_payroll_impulsion", deps={"l10n_be_hr_payroll"}, auto_install=True)
        # https://github.com/odoo/enterprise/commit/228a5b68428d6bd60a64309b190e95fec7b91e3a
        # https://github.com/odoo/enterprise/commit/6d85ecc920736b8976e4fa44b090f86fe9e2e384
        util.new_module(
            cr, "l10n_be_hr_payroll_variable_revenue", deps={"l10n_be_hr_payroll_account"}, auto_install=True
        )

        # https://github.com/odoo/enterprise/commit/6cd63c5c64073e38e4b90ea612a0928c23983df2
        util.new_module(cr, "l10n_cl_edi_stock", deps={"l10n_cl_edi", "sale_stock"}, auto_install=True)
        # https://github.com/odoo/enterprise/commit/88c394a12e8123f8bed0e18624b8ef4e55626200
        util.new_module(cr, "l10n_cl_edi_boletas", deps={"l10n_cl_edi"})
        # This is NOT a module to remove the reports...
        # https://github.com/odoo/enterprise/commit/8df67107c649e10fe258610ea5652f817ce9b791
        util.new_module(cr, "l10n_no_reports", deps={"l10n_no", "account_reports"}, auto_install=True)

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

        # https://github.com/odoo/enterprise/pull/19376
        util.new_module(cr, "l10n_mx_xml_polizas", deps={"l10n_mx_reports"}, auto_install=True)

        # https://github.com/odoo/enterprise/pull/21591
        util.new_module(
            cr, "l10n_mx_edi_stock_extended", deps={"l10n_mx_edi_extended", "l10n_mx_edi_stock"}, auto_install=True
        )

        # module added in stable after release, but need to installed if user didn't do it in previous version
        # Actually, it should be as it doesn't works without...
        util.trigger_auto_install(cr, "account_online_synchronization")

        util.merge_module(cr, "pos_hr_l10n_be", "pos_blackbox_be")
        util.module_deps_diff(cr, "pos_blackbox_be", plus={"pos_hr"}, minus={"pos_cash_rounding"})

        # https://github.com/odoo/enterprise/pull/23728 (fw)
        util.trigger_auto_install(cr, "l10n_lu_reports_annual_vat")

        # https://github.com/odoo/enterprise/pull/23535
        util.new_module(cr, "account_avatax", deps={"payment", "account"})
        util.new_module(cr, "account_avatax_sale", deps={"account_avatax", "sale"}, auto_install=True)
        util.new_module(
            cr, "account_avatax_sale_subscription", deps={"account_avatax_sale", "sale_subscription"}, auto_install=True
        )
        util.new_module(
            cr, "website_sale_account_avatax", deps={"account_avatax_sale", "website_sale"}, auto_install=True
        )

        # https://github.com/odoo/enterprise/pull/34563
        util.new_module(cr, "l10n_de_datev_reports", deps={"l10n_de_reports"}, auto_install=True)

        # https://github.com/odoo/enterprise/pull/38500/
        util.new_module(cr, "data_merge_stock_account", deps={"data_merge", "stock_account"}, auto_install=True)

        # https://github.com/odoo/enterprise/pull/23158
        util.new_module(cr, "l10n_pe_edi_stock", deps={"delivery", "l10n_pe_edi"}, auto_install=True)

        # https://github.com/odoo/enterprise/pull/34648
        util.new_module(cr, "l10n_pe_edi_stock_20", deps={"l10n_pe_edi_stock"}, auto_install=True)

        # https://github.com/odoo/odoo/pull/80214
        util.new_module(cr, "l10n_sa_pos", deps={"l10n_gcc_pos", "l10n_sa_invoice"}, auto_install=True)

        # https://github.com/odoo/enterprise/pull/27675
        util.new_module(cr, "l10n_mx_edi_40", deps={"l10n_mx_edi"}, auto_install=True)
        util.new_module(cr, "l10n_mx_edi_stock_40", deps={"l10n_mx_edi_40", "l10n_mx_edi_stock"}, auto_install=True)
        util.new_module(
            cr,
            "l10n_mx_edi_stock_extended_40",
            deps={"l10n_mx_edi_stock_40", "l10n_mx_edi_stock_extended"},
            auto_install=True,
        )

        # https://github.com/odoo/enterprise/pull/32866
        util.new_module(cr, "l10n_es_reports_2023", deps={"l10n_es_reports"}, auto_install=True)

        # https://github.com/odoo/enterprise/pull/29091
        util.new_module(cr, "l10n_mx_xml_polizas_edi", deps={"l10n_mx_edi", "l10n_mx_xml_polizas"}, auto_install=True)

        # https://github.com/odoo/enterprise/pull/35051
        util.new_module(cr, "l10n_lu_reports_annual_vat_2023", deps={"l10n_lu_reports_annual_vat"}, auto_install=True)

        # https://github.com/odoo/enterprise/pull/27675
        util.new_module(
            cr, "l10n_mx_edi_extended_40", deps={"l10n_mx_edi_40", "l10n_mx_edi_extended"}, auto_install=True
        )

        # https://github.com/odoo/enterprise/pull/43538
        util.new_module(cr, "delivery_ups_rest", deps={"delivery", "mail"})

        # https://github.com/odoo/enterprise/pull/18805
        util.new_module(cr, "account_reports_tax_reminder", deps={"account_reports"}, auto_install=True)

        # https://github.com/odoo/enterprise/pull/39079
        util.new_module(cr, "l10n_es_reports_2023_2", deps={"l10n_es_reports"}, auto_install=True)

        # https://github.com/odoo/enterprise/pull/19348
        util.new_module(cr, "l10n_be_reports_post_wizard", deps={"l10n_be_reports"}, auto_install=True)

    util.remove_module(cr, "website_gengo")
    util.remove_module(cr, "base_gengo")

    # implicit dependency, see odoo/odoo@e2dc415c46e5839173b26d1d19719aaed8dbba51
    if util.module_installed(cr, "sale_stock_margin"):
        util.force_install_module(cr, "sale_stock")
