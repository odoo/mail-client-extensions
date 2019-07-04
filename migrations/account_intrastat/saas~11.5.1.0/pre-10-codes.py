# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):

    # Change old model -> new one
    # Doing this avoid to alter account.invoice.line
    util.rename_model(cr, "report.intrastat.code", "account.intrastat.code")
    if util.module_installed(cr, "l10n_be_intrastat"):
        cr.execute("alter table l10n_be_intrastat_transaction DROP CONSTRAINT l10n_be_intrastat_transaction_l10n_be_intrastat_trcodeunique")

    # This way, we avoid to move value from name to code for thousands of records
    util.rename_field(cr, "account.intrastat.code", "name", "code")
    util.create_column(cr, "account_intrastat_code", "name", "varchar")
    util.create_column(cr, "account_intrastat_code", "type", "varchar")
    cr.execute("update account_intrastat_code set type='commodity'")

    # change xmlids
    if util.module_installed(cr, "l10n_be_intrastat"):
        cr.execute(
            r"""
            UPDATE ir_model_data
               SET module='account_intrastat',
                     name='commodity_code_2018_' || substring(name, 25)
             WHERE module='l10n_be_intrastat'
               AND name LIKE 'intrastat\_category\_2014\_%'
        """
        )

        util.move_field_to_module(cr, "account.invoice", "intrastat_country_id", "l10n_be_intrastat", "account_intrastat")
        util.move_field_to_module(cr, "product.category", "intrastat_id", "l10n_be_intrastat", "account_intrastat")
        util.move_field_to_module(cr, "res.company", "incoterm_id", "l10n_be_intrastat", "account_intrastat")
    else:
        util.create_column(cr, "account_invoice", "intrastat_country_id", "int4")
        cr.execute(
            """
            WITH intrastat_invoices AS (
                SELECT c.id AS country, i.id AS id
                  FROM account_invoice i
                  JOIN res_partner p ON p.id = CASE WHEN i.type IN ('out_invoice', 'out_refund')
                                                    THEN i.partner_shipping_id
                                                    ELSE i.partner_id
                                                END
                  JOIN res_country c ON (p.country_id = c.id AND c.intrastat = true)
            )
            UPDATE account_invoice inv
               SET intrastat_country_id = ii.country
              FROM intrastat_invoices ii
             WHERE ii.id = inv.id
        """
        )
