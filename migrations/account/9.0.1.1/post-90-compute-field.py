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
    # Compute matched_percentage on account_move
    cr.execute("""UPDATE account_move m
                    SET matched_percentage = CASE WHEN t2.total_amount = 0 THEN 1.0 ELSE t2.total_reconciled/t2.total_amount END
                    FROM (SELECT aml.move_id, sum(round(abs(aml.balance),4)) AS total_amount,
                                sum(round(abs(aml.balance),4)-round(abs(aml.amount_residual),4)) AS total_reconciled
                            FROM account_move_line aml, account_account a
                            WHERE a.id = aml.account_id AND a.internal_type IN ('receivable', 'payable')
                            GROUP BY move_id) AS t2
                    WHERE t2.move_id = m.id
            """)

    cr.execute("""UPDATE account_move m SET matched_percentage = 1 WHERE matched_percentage IS NULL""")

    # Compute debit_cash_basis, credit_cash_basis and balance_cash_basis on account_move_line

    cr.execute("""UPDATE account_move_line aml
                    SET debit_cash_basis = CASE WHEN j.type in ('sale', 'purchase') THEN aml.debit ELSE aml.debit*move.matched_percentage END,
                        credit_cash_basis = CASE WHEN j.type in ('sale', 'purchase') THEN aml.credit ELSE aml.credit*move.matched_percentage END,
                        balance_cash_basis = CASE WHEN j.type in ('sale', 'purchase') THEN aml.balance ELSE (aml.debit*move.matched_percentage) - (aml.credit*move.matched_percentage) END
                    FROM account_move move, account_journal j
                    WHERE aml.move_id = move.id AND aml.journal_id = j.id
            """)

    # Compute other fields via ORM
    # If slow, see below for a way to bootstrap these fields using a specific upgrade script
    # https://github.com/odoo/migration-scripts/commit/f4caab2e581d87d03a6f3d0399686dc4a411ad2b#diff-a9eb42ce1e369248e123f58aeb36443f
    query = """SELECT id FROM account_move_line WHERE amount_residual IS NULL"""
    util.recompute_fields(
        cr,
        "account.move.line",
        fields=("amount_residual", "amount_residual_currency", "reconciled"),
        query=query,
    )

    query = """SELECT inv.id FROM account_invoice inv, res_company c
                    WHERE c.id = inv.company_id and c.currency_id != inv.currency_id
                """
    util.recompute_fields(
        cr,
        "account.invoice",
        fields=("amount_total_company_signed", "amount_total_signed", "amount_untaxed_signed"),
        query=query,
    )

    # aml field will trigger the computation of residual field on invoice
    """ In some case, it is possible that we have some entries that were not reconcile correctly due to them being in different currency
        (change error). In this case, we just create an entry with debit=credit=0 and amount_currency being the inverse of what remains to reconcile
        and we reconcile this line with the one that should have been reconciled """
    env = util.env(cr)
    cr.execute("""SELECT id FROM account_move_line WHERE reconcile_id is NOT NULL and reconciled = false""")
    ids = [row[0] for row in cr.fetchall()]
    amls = env["account.move.line"].browse(ids)
    cr.execute("""SELECT id, period_lock_date, fiscalyear_lock_date from res_company""")
    info_period = cr.dictfetchall()
    cr.execute("""UPDATE res_company set period_lock_date = '1990-01-01', fiscalyear_lock_date = '1990-01-01'""")
    cr.execute("""CREATE TABLE account_move_line_reconcile_temp AS table account_move_line WITH NO DATA""")

    for aml in amls:
        if aml.amount_residual_currency:
            cr.execute(
                """INSERT INTO account_move_line_reconcile_temp
                (SELECT * FROM account_move_line where id = %s)""",
                [aml.id],
            )
            cr.execute(
                """UPDATE account_move_line_reconcile_temp
                SET id = nextval('account_move_line_id_seq'), credit = 0, debit = 0, balance = 0, amount_currency = %s, amount_residual_currency = %s
                WHERE id = %s RETURNING id""",
                [-aml.amount_residual_currency, -aml.amount_residual_currency, aml.id],
            )
            (aml_copy_id,) = cr.fetchone()
            cr.execute(
                """INSERT INTO account_move_line (SELECT * FROM account_move_line_reconcile_temp where id = %s)""",
                [aml_copy_id],
            )
            aml_copy = env["account.move.line"].browse(aml_copy_id)
            cr.execute(
                """
                INSERT INTO account_partial_reconcile (
                    debit_move_id, credit_move_id, amount, amount_currency, company_id, currency_id)
                VALUES (
                    %s, %s, %s, %s, %s, %s)""",
                (aml.id, aml_copy.id, 0, aml.amount_residual_currency, aml.company_id.id, aml.currency_id.id),
            )
            cr.execute(
                """
                UPDATE account_move_line set amount_residual = 0, amount_residual_currency = 0, reconciled=true WHERE id in %s""",
                [(aml.id, aml_copy.id)],
            )
    for el in info_period:
        cr.execute(
            """UPDATE res_company
                        SET period_lock_date = %s, fiscalyear_lock_date = %s
                        WHERE id = %s""",
            [el["period_lock_date"], el["fiscalyear_lock_date"], el["id"]],
        )
    cr.execute("""DROP TABLE account_move_line_reconcile_temp""")

    cr.execute("""UPDATE wkf_transition SET condition='reconciled' WHERE condition = 'False and reconciled'""")
    cr.execute("""UPDATE wkf_transition SET condition='not reconciled' WHERE condition = 'False and not reconciled'""")

    # Check that we don't have any invoices that have not been calculated by the orm
    # If we do, it is an error and it is possible that someone has create the invoice with an account not reconciliable and we should
    # warn the user that he should do smth about that
    cr.execute("""SELECT id FROM account_invoice WHERE state = 'open' and residual_signed IS NULL""")
    invoices = cr.fetchall()
    if len(invoices) != 0:
        cr.execute("""
            SELECT inv.id FROM account_invoice inv, account_account a
            WHERE inv.account_id = a.id AND a.reconcile = 'f'
        """)
        unrecs = cr.fetchall()
        if unrecs:
            msg_unrecs = (
                "\n{count_unrec} of them (ID:{unrec_ids}) have been set on unreconciliable accounts, which is wrong"
            ).format(count_unrec=len(unrecs), unrec_ids=[row[0] for row in unrecs])
        else:
            msg_unrecs = (
                "\nNo invoices were set on unreconciliable accounts. You need "
                "to search in another direction."
                "\neg: - no account move line for this invoice"
                "\n    - invoice on an opening/closing period that has been removed"
            )
        msg = (
            "{count_inv} invoices have not been correctly computed. please "
            "check them as it probably means a huge user mistake that needs "
            "attention. ID: {faulty_ids}{msg_unrecs}"
        ).format(
            count_inv=len(invoices),
            faulty_ids=[row[0] for row in invoices],
            msg_unrecs=msg_unrecs,
        )
        util.add_to_migration_reports(msg, "Accounting")
