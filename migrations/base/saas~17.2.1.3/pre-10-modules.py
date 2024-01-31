# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "account_taxcloud"):
        # Archive taxcloud fiscal positions because they will no longer work.
        cr.execute("UPDATE account_fiscal_position SET active = false WHERE is_taxcloud")

        # Don't delete the included fiscal position (could be used).
        cr.execute(
            """
            DELETE FROM ir_model_data
                  WHERE module = 'account_taxcloud'
                    AND name = 'account_fiscal_position_taxcloud_us'
            """
        )

        util.add_to_migration_reports(
            """
                <p><strong>IMPORTANT NOTICE</strong></p>
                <p>
                    Taxcloud is no longer supported in this version of Odoo and has been uninstalled. This doesn't
                    affect existing, captured Taxcloud transactions that may exist in your database.

                    See <a href="https://www.odoo.com/documentation/17.0/applications/finance/accounting/taxes/taxcloud.html">our documentation</a>
                    for more info and recommendations.
                </p>
            """,
            category="Accounting",
            format="html",
        )

    taxcloud_modules = (
        "account_taxcloud",
        "sale_account_taxcloud",
        "sale_amazon_taxcloud",
        "sale_loyalty_taxcloud",
        "sale_loyalty_taxcloud_delivery",
        "sale_subscription_taxcloud",
        "website_sale_account_taxcloud",
    )
    for module in taxcloud_modules:
        util.remove_module(cr, module)

    util.merge_module(cr, "l10n_fr_fec", "l10n_fr")

    util.merge_module(cr, "account_payment_term", "account")

    util.merge_module(cr, "account_reports_tax_reminder", "account_reports")

    util.merge_module(cr, "stock_landed_costs_company", "stock_landed_costs")

    util.merge_module(cr, "l10n_es_edi_facturae_invoice_period", "l10n_es_edi_facturae")

    util.rename_module(cr, "l10n_fr", "l10n_fr_account")  # nofml
    util.force_migration_of_fresh_module(cr, "l10n_fr")

    util.merge_module(cr, "l10n_dk_audit_trail", "l10n_dk")

    util.remove_module(cr, "l10n_dk_edi")
