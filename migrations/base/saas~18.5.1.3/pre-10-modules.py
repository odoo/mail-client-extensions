import logging

from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "pos_paytm"):
        cr.execute("SELECT 1 FROM pos_payment_method WHERE payment_method_type = 'paytm' LIMIT 1")
        if cr.rowcount:
            util.add_to_migration_reports(
                """
                    <p><strong>REMOVED MODULE: POS PayTM</strong></p>
                    <p>
                        The <code>pos_paytm</code> module has been removed during the upgrade, as it is no longer supported.
                        <br/>
                        Please refer to <a href="https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/payment_methods/terminals.html">
                        the latest POS terminal integration options</a> to reconfigure supported payment terminals.
                    </p>
                """,
                category="Point Of Sale",
                format="html",
            )
    util.remove_module(cr, "pos_paytm")
    if util.modules_installed(cr, "account_budget"):
        util.force_install_module(cr, "account_budget_purchase")
    util.merge_module(cr, "l10n_be_reports_prorata", "l10n_be_reports")
    util.merge_module(cr, "account_edi_ubl_cii_tax_extension", "account_edi_ubl_cii")
    util.merge_module(cr, "l10n_be_hr_payroll_dmfa_sftp", "l10n_be_hr_payroll")

    util.merge_module(cr, "l10n_id_efaktur_coretax", "l10n_id_efaktur")  # nofml
    util.rename_module(cr, "l10n_id_efaktur", "l10n_id_efaktur_coretax")

    util.merge_module(cr, "l10n_pl_taxable_supply_date", "l10n_pl")

    util.remove_module(cr, "test_ai")
    util.merge_module(cr, "l10n_it_edi_withholding", "l10n_it_edi")
    util.rename_module(cr, "account_auto_transfer", "account_transfer")

    util.merge_module(cr, "pos_epson_printer", "point_of_sale")
    util.merge_module(cr, "pos_self_order_epson_printer", "pos_self_order")

    util.merge_module(cr, "l10n_it_edi_withholding_reports", "l10n_it_reports")
    util.merge_module(cr, "l10n_in_reports_gstr_document_summary", "l10n_in_reports")
    util.remove_module(cr, "website_payment_authorize")
    util.remove_module(cr, "ai_calendar")

    if util.modules_installed(cr, "ai"):
        util.force_install_module(cr, "ai_app")
        util.modules_auto_discovery(cr, force_installs=["ai_app"])

    util.remove_module(cr, "documents_hr_recruitment")
    util.merge_module(cr, "l10n_dk_rsu", "l10n_dk_reports")

    if util.has_enterprise():
        if not util.modules_installed(cr, "l10n_mx_hr_payroll_account"):
            util.add_to_migration_reports(
                """
                The module <i>Employees - Mexico</i> is now part of the <i>Mexico - Payroll with Accounting</i> module.
                You may re-install Mexico's payroll modules to use the new features.
                """,
                "Mexico Employees",
                format="html",
            )
            util.uninstall_module(cr, "l10n_mx_hr")
        util.rename_module(cr, "l10n_mx_hr", "l10n_mx_hr_payroll_account_edi")
    else:
        if util.modules_installed(cr, "l10n_mx_hr"):
            util.add_to_migration_reports(
                "The module <i>Employees - Mexico</i> is no longer available in Odoo Community.",
                "Mexico Employees",
                format="html",
            )
        util.remove_module(cr, "l10n_mx_hr")

    if util.has_enterprise():
        util.rename_module(cr, "account_disallowed_expenses", "account_fiscal_categories")
        util.rename_module(cr, "account_disallowed_expenses_fleet", "account_fiscal_categories_fleet")
        util.rename_module(cr, "l10n_be_disallowed_expenses", "l10n_be_fiscal_categories")
        util.rename_module(cr, "l10n_be_account_disallowed_expenses_fleet", "l10n_be_fiscal_categories_fleet")

    # account_base_import now depends on account_asset, this will install too many
    # account modules and subsequently trigger the auto-install of many more
    if util.module_installed(cr, "account_base_import") and not util.module_installed(cr, "account_asset"):
        cr.execute(
            """
            SELECT 1
              FROM ir_module_module_dependency d
              JOIN ir_module_module m
                ON d.module_id = m.id
             WHERE d.name = 'account_base_import'
               AND m.state IN %s
             LIMIT 1
            """,
            [util.INSTALLED_MODULE_STATES],
        )
        if not cr.rowcount:
            level = util.NEARLYWARN if util.on_CI() else logging.WARNING
            util._logger.log(level, "Uninstalling account_base_import to avoid auto-install of many accounting modules")
            util.uninstall_module(cr, "account_base_import")

    util.remove_module(cr, "web_editor")

    util.merge_module(cr, "l10n_it_xml_export", "l10n_it_reports")
    # since there is no real dependency between l10n_it_xml_export and l10n_it_reports
    util.force_upgrade_of_fresh_module(cr, "l10n_it_reports")
