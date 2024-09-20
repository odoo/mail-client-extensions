import os

from odoo.upgrade import util

ODOO_MIG_18_REMOVE_CONSOLIDATION = util.str2bool(os.getenv("ODOO_MIG_18_REMOVE_CONSOLIDATION"), "")


def migrate(cr, version):
    util.remove_module(cr, "web_tour_recorder")
    util.remove_module(cr, "account_lock")
    util.remove_module(cr, "l10n_bg_reports")

    if util.module_installed(cr, "account_consolidation"):
        if not ODOO_MIG_18_REMOVE_CONSOLIDATION:
            cr.execute("""
                SELECT 1
                FROM consolidation_period
                LIMIT 1
            """)

            if cr.rowcount:
                raise util.UpgradeError("""
                    The Consolidation app is removed in Odoo 18.0, in favour of the shared accounts feature.
                    Your database contains data for this app that cannot be migrated automatically.
                    All existing consolidation data will be lost ; you will be required to create a new configuration using the new feature.
                    Please contact us to proceed, or for additional information.
                """)

        util.add_to_migration_reports(
            """
            The Consolidation app has been removed. It is now replaced by the possibility
            to share accounts between companies, and directly consolidate them into your accounting reports.
            """,
            category="Accounting",
        )
        # TODO: Add a link to the doc once it is written

    util.remove_module(cr, "account_consolidation")
    util.remove_module(cr, "l10n_be_us_consolidation_demo")

    payment_types = ["alipay", "payulatam", "payumoney"]
    if util.module_installed(cr, "payment"):
        cr.execute(
            """
            UPDATE payment_provider
               SET state = 'disabled',
                   redirect_form_view_id = NULL
             WHERE code IN %s
            """,
            [tuple(payment_types)],
        )
        util.change_field_selection_values(
            cr,
            "payment.provider",
            "code",
            {payment: "none" for payment in payment_types},
        )

    modules_to_remove = [(f"payment_{payment}", "") for payment in payment_types]
    modules_to_remove.append(("sale_ebay", "Ebay sale connector is no longer maintained and will be removed."))
    for module, message in modules_to_remove:
        if util.module_installed(cr, module):
            if not message:
                util.add_to_migration_reports(
                    f"Previously deprecated module {module} has been removed.",
                    category="Payments",
                )
            else:
                util.add_to_migration_reports(message, category="Ebay Connector")
        util.remove_module(cr, module)

    util.rename_module(cr, "website_sale_picking", "website_sale_collect")

    if util.module_installed(cr, "payment"):
        cr.execute(
            """
            UPDATE payment_provider
               SET state = 'disabled',
                   redirect_form_view_id = NULL
             WHERE "code" IN ('ogone', 'sips')
            """
        )
        if util.module_installed(cr, "payment_ogone"):
            util.add_to_migration_reports(
                "The module 'Payment Provider: Ogone' has been removed, as Ogone is replaced by Worldline.",
                category="Payments",
            )
            # TODO EDM: auto-install payment_worldline and migrate existing payment.token records.
        if util.module_installed(cr, "payment_sips"):
            util.add_to_migration_reports(
                "The module 'Payment Provider: SIPS' has been removed, as SIPS is replaced by Worldline.",
                category="Payments",
            )
        util.change_field_selection_values(cr, "payment.provider", "code", {"ogone": "none", "sips": "none"})
    util.remove_module(cr, "payment_ogone")
    util.remove_module(cr, "payment_sips")

    util.merge_module(cr, "l10n_mx_edi_stock_extended_31", "l10n_mx_edi_stock_extended")
    util.merge_module(cr, "l10n_mx_edi_stock_extended", "l10n_mx_edi_stock")
    util.force_upgrade_of_fresh_module(cr, "html_editor", init=False)
    util.force_upgrade_of_fresh_module(cr, "l10n_br_edi_website_sale")
    if util.module_installed(cr, "mrp_account") and not util.module_installed(cr, "project"):
        # The following query identifies whether there is at least a BOM or a MO that has an analytic distribution
        # which contains exactly one line at 100%. If that's the case, we force the installation of the project module
        # because we will create for each BOM and MO that meets this condition, a project that has the same analytic
        # accounts as the ones from their analytic distribution, in order to preserve user data
        cr.execute("""
           (SELECT 1
              FROM mrp_production,
                   JSONB_EACH_TEXT(analytic_distribution)
          GROUP BY id
            HAVING COUNT(*) = 1
               AND SUM(value::numeric) = 100
             LIMIT 1)
             UNION
             (WITH _mrp_bom AS (
                   SELECT CAST(SPLIT_PART(res_id, ',', 2) AS INTEGER) AS id,
                          CAST(value_text AS jsonb) AS analytic_distribution
                     FROM _ir_property
                    WHERE name = 'analytic_distribution_text'
                      AND value_text != 'false'
                 )
            SELECT 1
              FROM _mrp_bom,
                   JSONB_EACH_TEXT(analytic_distribution)
          GROUP BY id
            HAVING COUNT(*) = 1
               AND SUM(value::numeric) = 100.0
             LIMIT 1)
        """)
        if cr.rowcount:
            util.add_to_migration_reports(
                "We introduced a new feature allowing projects to have multiple analytic accounts (one per plan). "
                "We then removed the analytic distribution of Manufacturing Orders and Bills of Materials "
                "and replaced it with a project field, whose analytic accounts represent the analytic distribution. "
                "For MOs and BOMs that had an analytic distribution containing exactly one line at 100%, new projects "
                "were created and linked to them. Each project will contain the same analytic accounts as in the "
                "analytic distribution of the MO/BOM to preserve user data.",
                "Manufacturing/Project/Analytic",
            )
            util.force_install_module(cr, "project_mrp")
            util.force_upgrade_of_fresh_module(cr, "project_mrp")

    util.remove_module(cr, "test_marketing_card")
    util.remove_module(cr, "mass_mailing_marketing_card")

    util.rename_module(cr, "account_sepa", "account_iso20022")
    util.rename_module(cr, "hr_payroll_account_sepa", "hr_payroll_account_iso20022")

    util.merge_module(cr, "l10n_ro_efactura", "l10n_ro_edi")

    if not util.has_enterprise():
        util.remove_module(cr, "spreadsheet_dashboard_purchase_stock")
    util.remove_module(cr, "spreadsheet_dashboard_purchase")

    util.force_migration_of_fresh_module(cr, "certificate")

    util.remove_module(cr, "l10n_account_customer_statements")
    util.remove_module(cr, "l10n_uk_customer_statements")

    if util.module_installed(cr, "l10n_in") and not util.module_installed(cr, "l10n_in_withholding"):
        cr.execute("""
            SELECT 1
              FROM account_move_line aml
              JOIN account_account_tag_account_move_line_rel aml_tag
                ON aml_tag.account_move_line_id = aml.id
              JOIN account_account_tag a_tag
                ON a_tag.id = aml_tag.account_account_tag_id
              JOIN account_report_expression arx
                ON a_tag.name->>'en_US' IN (CONCAT('+', arx.formula), CONCAT('-', arx.formula))
              JOIN ir_model_data ref
                ON ref.res_id = arx.id
               AND ref.model= 'account.report.expression'
             WHERE ref.name ILIKE '%tds_report_line_section%'
                OR ref.name ILIKE '%tcs_report_line_section%'
             LIMIT 1
        """)
        if cr.rowcount:
            util.force_install_module(cr, "l10n_in_withholding")
