# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    """
        During computation of fields.function that are stored, process is really slow due to
        a problem with the workflow transition that computes a lot of time a field which he should
        not. So for the sake of this migration, we will deactivate the transition before computing
        the stored fields and reactivate it after.
    """

    cr.execute("""UPDATE wkf_transition SET condition='False and reconciled' WHERE condition = 'reconciled'""")
    cr.execute("""UPDATE wkf_transition SET condition='False and not reconciled' WHERE condition = 'not reconciled'""")

    """
        In order to speed up migration, compute as many computed field as we can in sql before.
    """
    util.create_column(cr, 'account_move_line', 'balance', 'numeric')
    util.create_column(cr, 'account_move_line', 'company_currency_id', 'int4')
    util.create_column(cr, 'account_move_line', 'user_type_id', 'int4')
    util.create_column(cr, 'account_move_line', 'amount_residual', 'numeric')
    util.create_column(cr, 'account_move_line', 'amount_residual_currency', 'numeric')
    util.create_column(cr, 'account_move_line', 'reconciled', 'boolean')
    util.create_column(cr, 'account_move_line', 'debit_cash_basis', 'numeric')
    util.create_column(cr, 'account_move_line', 'credit_cash_basis', 'numeric')
    util.create_column(cr, 'account_move_line', 'balance_cash_basis', 'numeric')

    query = """
        UPDATE account_move_line aml
           SET balance = (aml.debit-aml.credit),
               company_currency_id = c.currency_id,
               user_type_id = acc.user_type,
               amount_residual = CASE WHEN acc.reconcile = false THEN 0 ELSE amount_residual END,
               amount_residual_currency = CASE WHEN acc.reconcile = false THEN 0 ELSE amount_residual_currency END,
               reconciled = CASE WHEN acc.reconcile = false THEN false ELSE reconciled END,
               debit_cash_basis = CASE WHEN j.type not in ('sale', 'purchase') THEN aml.debit ELSE NULL END,
               credit_cash_basis = CASE WHEN j.type not in ('sale', 'purchase') THEN aml.credit ELSE NULL END,
               balance_cash_basis = CASE WHEN j.type not in ('sale', 'purchase') THEN aml.debit-aml.credit ELSE NULL END
          FROM res_company c,
               account_account acc,
               account_journal j
         WHERE aml.company_id = c.id
           AND aml.account_id = acc.id
           AND aml.journal_id = j.id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_move_line", alias="aml"))

    # update aml that are from invoice that have been fully paid, meaning the aml are already reconciled
    query = """
        UPDATE account_move_line aml
           SET amount_residual = 0.0,
               amount_residual_currency = 0.0,
               reconciled = true
          FROM account_account acc,
               account_invoice inv
         WHERE aml.account_id = acc.id
           AND aml.move_id = inv.move_id
           AND acc.reconcile = true
           AND inv.state != 'open'
           AND aml.reconcile_id IS NOT NULL
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_move_line", alias="aml"))

    util.create_column(cr, 'account_invoice', 'residual_company_signed', 'numeric')
    util.create_column(cr, 'account_invoice', 'residual_signed', 'numeric')
    util.create_column(cr, 'account_invoice', 'residual', 'numeric')
    util.create_column(cr, 'account_invoice', 'reconciled', 'boolean')
    util.create_column(cr, 'account_invoice', 'amount_total_company_signed', 'numeric')
    util.create_column(cr, 'account_invoice', 'amount_total_signed', 'numeric')
    util.create_column(cr, 'account_invoice', 'amount_untaxed_signed', 'numeric')

    cr.execute("""UPDATE account_invoice inv
                    SET residual_signed = CASE WHEN state != 'open' THEN 0.0 ELSE NULL END,
                        residual_company_signed = CASE WHEN state != 'open' THEN 0.0 ELSE NULL END
                    """)

    cr.execute("""UPDATE account_invoice inv
                    SET amount_total_company_signed = CASE WHEN inv.type IN ('in_refund', 'out_refund')
                                                           THEN -inv.amount_total ELSE inv.amount_total END,
                        amount_total_signed = CASE WHEN inv.type IN ('in_refund', 'out_refund')
                                                   THEN -inv.amount_total ELSE inv.amount_total END,
                        amount_untaxed_signed = CASE WHEN inv.type IN ('in_refund', 'out_refund')
                                                     THEN -inv.amount_untaxed ELSE inv.amount_untaxed END
                    FROM res_company c
                    WHERE c.id = inv.company_id and c.currency_id = inv.currency_id
                """)

    cr.execute("""UPDATE account_invoice
                    SET move_name = internal_number
                    WHERE move_name='/' AND internal_number IS NOT NULL""")

    util.create_column(cr, 'account_move', 'amount', 'numeric')
    util.create_column(cr, 'account_move', 'matched_percentage', 'numeric')
    util.create_column(cr, 'account_move', 'currency_id', 'int4')

    cr.execute("""UPDATE account_move m
                    SET matched_percentage = NULL,
                        currency_id = c.currency_id,
                        amount = t2.debitSum
                    FROM (SELECT move_id, sum(debit) AS debitSum
                            FROM account_move_line
                            GROUP BY move_id) AS t2,
                        res_company c
                    WHERE t2.move_id = m.id AND m.company_id = c.id
                """)

    util.create_column(cr, 'account_invoice_line', 'currency_id', 'int4')

    cr.execute("""UPDATE account_invoice_line l
                    SET currency_id = i.currency_id
                    FROM account_invoice i
                    WHERE l.invoice_id = i.id
                """)

    util.create_column(cr, 'account_bank_statement', 'total_entry_encoding', 'numeric')
    util.create_column(cr, 'account_bank_statement', 'difference', 'numeric')

    cr.execute("""UPDATE account_bank_statement a
                    SET total_entry_encoding = b.amountSum,
                        difference = (a.balance_end_real - a.balance_end)
                    FROM (SELECT statement_id, sum(amount) AS amountSum
                            FROM account_bank_statement_line
                            GROUP BY statement_id) AS b
                    WHERE b.statement_id = a.id
                """)

    util.create_column(cr, 'account_invoice_tax', 'currency_id', 'int4')

    cr.execute("""UPDATE account_invoice_tax a
                    SET currency_id = b.currency_id
                    FROM account_invoice b
                    WHERE a.invoice_id = b.id
                """)

    util.create_column(cr, 'account_account', 'internal_type', 'varchar')

    util.create_m2m(cr, 'account_invoice_account_move_line_rel', 'account_invoice', 'account_move_line')

    cr.execute("""INSERT INTO account_invoice_account_move_line_rel
                    (SELECT i.id AS i_id, a.debit_move_id AS ml_id
                        FROM account_invoice i
                        JOIN account_move_line l ON (i.move_id = l.move_id)
                        JOIN account_partial_reconcile a ON (a.credit_move_id = l.id)
                    UNION
                    SELECT i.id AS i_id, a.credit_move_id AS ml_id
                        FROM account_invoice i
                        JOIN account_move_line l ON (i.move_id = l.move_id)
                        JOIN account_partial_reconcile a ON (a.debit_move_id = l.id))
        """)

    util.create_column(cr, 'account_journal', 'at_least_one_inbound', 'bool')
    util.create_column(cr, 'account_journal', 'at_least_one_outbound', 'bool')

    cr.execute("""UPDATE account_journal
                    SET at_least_one_outbound = false,
                        at_least_one_inbound = false
                """)
