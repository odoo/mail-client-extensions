# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):

    # ===========================================================
    # Currency on all account.move.line (PR:50711 & 10394)
    # ===========================================================

    util.remove_field(cr, 'account.move.line', 'always_set_currency_id')

    cr.execute('''
        ALTER TABLE account_move_line
        DROP CONSTRAINT account_move_line_check_amount_currency_balance_sign
    ''')

    cr.execute('''
        UPDATE account_move_line
        SET 
            currency_id = company_currency_id,
            amount_currency = balance
        WHERE currency_id IS NULL
    ''')

    # Prevent inconsistencies in others scripts by adding the updated constraint manually.
    cr.execute('''
        ALTER TABLE account_move_line 
        ADD CONSTRAINT account_move_line_check_amount_currency_balance_sign 
        CHECK(
            (
                (currency_id != company_currency_id)
                AND
                (
                    (debit - credit <= 0 AND amount_currency <= 0)
                    OR
                    (debit - credit >= 0 AND amount_currency >= 0)
                )
            )
            OR
            (
                currency_id = company_currency_id
                AND
                ROUND(debit - credit - amount_currency, 2) = 0
            )
        )
    ''')

    # ===========================================================
    # Fiscal country field on companies (PR 55308 & 12156)
    # ===========================================================
    util.create_column(cr, 'res_company', 'account_tax_fiscal_country_id', 'int4')

    # If a fiscal country was set with the dedicated config parameter, use it; else use the company's country.
    cr.execute("""
        UPDATE res_company
        SET account_tax_fiscal_country_id = COALESCE(parameter_country.id, company_partner.country_id)
        FROM res_partner company_partner
        JOIN res_company company on company.partner_id = company.partner_id
        LEFT JOIN ir_config_parameter fiscal_country_param ON fiscal_country_param.key = CONCAT('account_fiscal_country_', company.id)
        LEFT JOIN res_country parameter_country ON LOWER(parameter_country.code) = LOWER(fiscal_country_param.value)
        WHERE res_company.id = company.id

    """)

    # Remove the fiscal country config parameters; now useless.
    cr.execute("""
        DELETE FROM ir_config_parameter
        WHERE key LIKE 'account_fiscal_country_%'
    """)

    # Replace the old related fields which pointed towards company country for use in taxes
    util.rename_field(cr, 'account.move.line', 'country_id', 'tax_fiscal_country_id')
    util.rename_field(cr, 'account.tax', 'country_id', 'tax_fiscal_country_id')
    util.rename_field(cr, 'account.tax.repartition.line', 'country_id', 'tax_fiscal_country_id')
