# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    util.create_column(cr, "account_tax", "is_base_affected", "boolean", default=True)
    util.create_column(cr, "account_tax_template", "is_base_affected", "boolean", default=True)

    util.create_column(cr, "account_chart_template", "account_journal_payment_debit_account_id", "int4")
    util.create_column(cr, "account_chart_template", "account_journal_payment_credit_account_id", "int4")
    util.create_column(cr, "res_company", "account_journal_payment_debit_account_id", "int4")
    util.create_column(cr, "res_company", "account_journal_payment_credit_account_id", "int4")

    util.move_field_to_module(cr, "res.config.settings", "transfer_account_id", "account_accountant", "account")

    # ===============================================================
    # Multi-VAT tax reports (PR: 68349)
    # ===============================================================
    util.rename_field(cr, "res.company", "account_tax_fiscal_country_id", "account_fiscal_country_id")
    util.remove_field(cr, "res.company", "account_tax_next_activity_type")
    util.remove_field(cr, "account.move.line", "tax_fiscal_country_id")
    util.remove_field(cr, "account.tax.repartition.line", "tax_fiscal_country_id")
    util.create_column(cr, "account_chart_template", "country_id", "int4")
    util.create_column(cr, "account_fiscal_position", "foreign_vat", "varchar")
    util.rename_field(cr, "account.tax", "tax_fiscal_country_id", "country_id")
    util.create_column(cr, "account_tax", "country_id", "int4")

    # We need the fiscal country to populate the taxes' country. It should've been guessed in pre-09.py already.

    # Initialize account.tax's country_id with the fiscal country of the company
    cr.execute(
        """
        UPDATE account_tax tax
           SET country_id = company.account_fiscal_country_id
          FROM res_company company
         WHERE tax.company_id = company.id
        """
    )

    # ===============================================================
    # Carry over tax grids between periods (PR:58523 & 13230)
    # ===============================================================

    util.create_column(cr, "account_tax_report_line", "carry_over_condition_method", "varchar")
    util.create_column(cr, "account_tax_report_line", "carry_over_destination_line_id", "int4")

    # ===============================================================
    # Payments Form View Improvement (PR:66069 & 16308 )
    # ===============================================================
    util.create_column(cr, "account_move", "amount_total_in_currency_signed", "numeric")
    query = """
        UPDATE account_move
           SET amount_total_in_currency_signed =
               CASE WHEN move_type = 'entry' THEN ABS(amount_total)
                    WHEN move_type IN ('in_invoice', 'out_refund', 'in_receipt') THEN -amount_total
                    ELSE amount_total
                END
        """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_move"))
    util.create_column(cr, "account_payment", "paired_internal_transfer_payment_id", "int4")
    util.create_column(cr, "account_payment", "destination_journal_id", "int4")

    util.remove_record(cr, "account.invoice_send")

    # set partner_id on internal transfer aml, (at least) needed for AccountPayment._seek_for_lines()
    query = """
        UPDATE account_move_line AS aml
           SET partner_id = pay.partner_id
          FROM account_payment pay
         WHERE pay.is_internal_transfer = TRUE
           AND aml.partner_id IS NULL
           AND pay.move_id = aml.move_id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_move_line", alias="aml"))
    # set destination_journal_id if one can be found via reconciled aml
    query = """
         UPDATE account_payment AS pay
            SET destination_journal_id = rec_aml.journal_id
           FROM account_move_line rec_aml
           JOIN account_partial_reconcile rec ON rec.debit_move_id = rec_aml.id OR rec.credit_move_id = rec_aml.id
           JOIN account_move_line aml ON (aml.debit > 0 AND rec.credit_move_id = rec_aml.id)
                                      OR (aml.credit > 0 AND rec.debit_move_id = rec_aml.id)
          WHERE pay.is_internal_transfer = TRUE
            AND pay.move_id = aml.move_id
            AND (
                    (pay.payment_type = 'outbound' AND rec.debit_move_id = aml.id)
                 OR (pay.payment_type = 'inbound' AND rec.credit_move_id = aml.id)
            )
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_payment", alias="pay"))
