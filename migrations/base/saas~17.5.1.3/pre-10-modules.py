import os

from odoo.upgrade import util

ODOO_MIG_18_REMOVE_CONSOLIDATION = util.str2bool(os.getenv("ODOO_MIG_18_REMOVE_CONSOLIDATION"), "1")


def migrate(cr, version):
    util.remove_module(cr, "web_tour_recorder")
    util.remove_module(cr, "account_lock")
    util.remove_module(cr, "l10n_bg_reports")

    if util.module_installed(cr, "account_consolidation"):
        cr.execute("""
            SELECT 1
              FROM consolidation_period
             LIMIT 1
        """)
        if not cr.rowcount:
            util.add_to_migration_reports(
                """
                <p>
                The Consolidation app has been removed. It is now replaced by the possibility
                to share accounts between companies, and directly consolidate them into your accounting reports.
                For more information on how account consolidations work in the new version, please refer to the
                <a href="https://www.odoo.com/documentation/18.0/applications/finance/accounting/get_started/consolidation.html">
                online documentation</a>.
                </p>
                """,
                category="Accounting",
                format="html",
            )
        else:
            if not ODOO_MIG_18_REMOVE_CONSOLIDATION:
                raise util.UpgradeError("""
                    The Consolidation app is removed in Odoo 18.0, in favour of the shared accounts feature.
                    Your database contains data for this app that cannot be migrated automatically.
                    All existing consolidation data will be lost ; you will be required to create a new configuration using the new feature.
                    Please set ODOO_MIG_18_REMOVE_CONSOLIDATION to 1 to proceed.
                    There is extra information about how to do account consolidation in Odoo 18.0 at
                    https://www.odoo.com/documentation/18.0/applications/finance/accounting/get_started/consolidation.html
                """)

            util.add_to_migration_reports(
                """
                <details>
                    <summary><strong class="text-danger">CONSOLIDATION APP REMOVED</strong> as of 18.0 - Transitioning to the New Shared Accounts Feature
                    in Odoo 18.0 <span class="text-info">(click to expand details)</span></summary>
                    <p>
                    Since the <strong>Consolidation</strong> app has been completely redesigned and no longer exists in Odoo <strong>18.0</strong>,
                    it is not possible to migrate the associated data. As a result, we have <string>uninstalled the application by default</strong>
                    in the new version.
                    <br/>
                    However, <strong>you might need to save key financial data before the upgrade and reconfigure your post-upgrade setup</strong>.
                    Below, you'll find a <strong>step-by-step</strong> guide on what to retain before upgrading:
                    </p>
                    <h3>1. Before the Upgrade</h3>
                    <p>Before proceeding with the upgrade, ensure you export the necessary data to avoid data loss. <i>Should the upgrade have
                    already been performed in production before the export, you can still request a backup within three months post-upgrade.
                    No rollback is allowed, the backup is for reference purposes only.</i></p>
                    <h4>1.1. Export Consolidation Mappings</h4>
                    <p>In Odoo 18.0, account mapping will still be essential, but the approach will be different. Retaining your previous mappings
                    will help you restructure your setup.</p>
                    <ul>
                        <li>Activate the developer mode then Go to Consolidation > Configuration > Consolidation account.</li>
                        <li>Export your Account Mappings, including all fields (! Field 'Accounts (account_ids)' should be part of the export)</li>
                        <li>Save this data in a structured format (CSV/XLSX).</li>
                    </ul>
                    <h4>1.2. Export Consolidated Financial Reports</h4>
                    <p>This will serve as a reference when reconfiguring reports post-upgrade.</p>
                    <ul>
                        <li>Download the latest consolidated Balance Sheet and P&L Statement in Excel/PDF format.</li>
                        <li>From your consolidation dashboard, download all your consolidated reports on specific dates (in pdf or in xlsx format)
                        [<a href="https://drive.google.com/file/d/11J-GdltYXJL_V1SsSc1OFgvRLzhc-2Q6/view">demo</a>]</li>
                        <li>Take note of key figures and structures for comparison after the reconfiguration.</li>
                    </ul>
                    <h3>2. Post-upgrade: Reconfigure</h3>
                    <h4>2.1. Configure Account Mapping</h4>
                    <p>Since Odoo 18.0, you must manually reconfigure mappings:</p>
                    <ul>
                        <li>Go to Accounting > Configuration > Chart of Accounts.</li>
                        <li>Click on view > in the tab 'mapping', mention the account code from your other company  </li>
                        <li>Select the account of your chart of accounts and go to the 'mapping' tab.
                        [<a href="https://drive.google.com/file/d/12NLAR-ytRcmiPoQ5s9k2jONuDsaa1qq8/view">demo</a>]</li>
                        <li>Based on the mapping you exported (1.1) add the code linked to the other companies. Refer to our
                        <a href="https://www.odoo.com/documentation/18.0/applications/finance/accounting/get_started/consolidation.html#import-a-mapping">
                        online documentation</a></li>
                    </ul>
                    <h4>2.2. (Re)-create Multi-Ledgers for Consolidation</h4>
                    <h4>2.3. Enable horizontal group on 'company' in the accounting reports</h4>
                    <h4>2.4. Reapply Currency Conversion for Consolidation</h4>
                    <p>Refer to our <a href="https://www.odoo.com/documentation/18.0/applications/finance/accounting/get_started/consolidation.html">
                    online documentation</a></p>
                    <h4>2.5 Consolidation reports</h4>
                    <p>As from Odoo 18, the consolidation reports will be made through the accounting application > reporting > Balance sheet or Profit and Loss.
                    <br/>If you were using other reportings within your consolidation app, you need to recreate it via the menu configuration > Accounting Reports
                    (activate first the debug mode).</p>
                    <h3>3. Final Validation & Best Practices</h3>
                    <ul>
                        <li>Compare pre-upgrade and post-upgrade reports to ensure accuracy.</li>
                        <li>Keep an archived copy of your exported mappings and reports in case reconfiguration is needed.</li>
                    </ul>
                </details>
                """,
                category="Accounting",
                format="html",
            )

    util.remove_module(cr, "account_consolidation")
    if util.module_installed(cr, "l10n_be_us_consolidation_demo"):
        cr.execute(
            """
            UPDATE ir_model_data
               SET module = '__export__'
             WHERE module = 'l10n_be_us_consolidation_demo'
               AND model IN ('account.account', 'account.move','mail.activity')
            """
        )
    util.remove_module(cr, "l10n_be_us_consolidation_demo")

    payment_types = ["alipay", "payulatam", "payumoney"]
    if util.module_installed(cr, "payment"):
        util.delete_unused(
            cr, *[f"payment_{ptype}.payment_provider_{ptype}" for ptype in payment_types], keep_xmlids=False
        )
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
            dict.fromkeys(payment_types, "none"),
        )

    modules_to_remove = [(f"payment_{payment}", "") for payment in payment_types]
    modules_to_remove.append(("sale_ebay", "Ebay sale connector is no longer maintained and will be removed."))
    util.delete_unused(cr, "sale_ebay.product_category_ebay", keep_xmlids=False)
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
    util.rename_module(cr, "l10n_es_pos_tbai", "l10n_es_edi_tbai_pos")

    # Ogone uses the same API as Worldline, with the same credentials. We modify the providers so that they continue
    # working. Payment tokens can thus remain untouched and will continue to work through Worldline.
    util.rename_module(cr, "payment_ogone", "payment_worldline")

    if util.module_installed(cr, "payment_sips"):
        cr.execute("UPDATE payment_provider SET redirect_form_view_id = NULL WHERE code = 'sips'")
        cr.execute("UPDATE payment_provider SET state = 'disabled' WHERE code = 'sips' AND state = 'enabled'")
        if cr.rowcount:
            util.add_to_migration_reports(
                "The module 'Payment Provider: SIPS' has been removed, as SIPS is replaced by Worldline.",
                category="Payments",
            )
    util.remove_module(cr, "payment_sips")

    util.merge_module(cr, "l10n_mx_edi_stock_extended_31", "l10n_mx_edi_stock_extended")
    util.merge_module(cr, "l10n_mx_edi_stock_extended", "l10n_mx_edi_stock")
    util.force_upgrade_of_fresh_module(cr, "l10n_mx_edi_extended")  # new dep of `l10n_mx_edi_stock`; needs bootstraping
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
                     FROM ir_property
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

    # Rename OCA module 'sale_commission' to 'sale_commission_oca'
    cr.execute(
        """
        SELECT 1
          FROM ir_module_module
         WHERE name = 'sale_commission'
           AND author ILIKE '%Odoo Community Association (OCA)%'
        """
    )
    if cr.rowcount:
        util.rename_module(cr, "sale_commission", "sale_commission_oca")

    if util.module_installed(cr, "l10n_us_hr_payroll") and not util.module_installed(cr, "base_address_extended"):
        util.force_upgrade_of_fresh_module(cr, "base_address_extended")

    if util.module_installed(cr, "l10n_ae_hr_payroll") and not util.module_installed(cr, "calendar"):
        # l10n_ae_hr_payroll now depends on hr_work_entry_holidays which depends (multi-level) on calendar
        util.create_column(cr, "res_partner", "calendar_last_notif_ack", "timestamp", default="now")
