# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util
import os


def migrate(cr, version):
    cr.execute(
        """
        SELECT array_agg(id ORDER BY id)
          FROM account_invoice
         WHERE state IN ('draft', 'cancel')
           AND move_id IS NOT NULL
    """
    )
    [inconsistent_invoice_ids] = cr.fetchone()
    if inconsistent_invoice_ids:
        inconsistent_invoice_ids = set(inconsistent_invoice_ids)
        # Try to fix the inconsistencies automatically

        # 1. The move associated to the invoice has the same total.
        #    Mark the invoice has open instead of draft/cancelled if the move is posted,
        #    otherwise let the former draft/cancel state, but remove it from the inconsistent invoices list
        #    to let the invoice line <-> move line mapping do its job.
        cr.execute(
            """
                   UPDATE account_invoice invoice
                      SET state = CASE WHEN same_amount_move.state = 'posted' THEN 'open' ELSE invoice.state END
                     FROM (
                               SELECT invoice.id as invoice_id, move.state, invoice.number, invoice.date_invoice
                                 FROM account_invoice invoice
                                 JOIN account_move move ON move.id = invoice.move_id
                                 JOIN account_journal journal ON journal.id = invoice.journal_id
                                 JOIN res_company company ON company.id = journal.company_id
                            LEFT JOIN account_move_line move_line ON move_line.move_id = move.id
                                WHERE invoice.state in ('draft', 'cancel')
                                  AND invoice.move_id IS NOT NULL
                             GROUP BY invoice.id, move.id
                               HAVING ROUND(SUM(
                                            CASE
                                            WHEN debit > 0
                                            THEN
                                                CASE
                                                WHEN move_line.currency_id != company.currency_id
                                                THEN amount_currency
                                                ELSE debit
                                                END
                                            ELSE 0
                                            END
                                      ), 2) = ROUND(invoice.amount_total, 2)
                          ) as same_amount_move
                    WHERE same_amount_move.invoice_id = invoice.id
                RETURNING id, invoice.number, invoice.date_invoice
            """
        )
        same_amount = cr.fetchall()
        if same_amount:
            inconsistent_invoice_ids -= set([r[0] for r in same_amount])
            util.add_to_migration_reports(
                f"""
                    <details>
                    <summary>
                        {len(same_amount)} draft and cancelled invoices were linked to accounting entries having the
                        same total. Normally, draft and cancelled invoices should not have entries in the accounting.
                        To be able to upgrade properly, these invoices have been marked as "Open" if their entry in the
                        accounting was posted. If the entry was unposted, than the invoice has been left as
                        draft/cancelled. Anyhow, you should really give it a look to make sure everything is correct.
                    </summary>
                    Invoices: {", ".join(f"{number}({date})" for _, number, date in same_amount)}
                    </details>
                """,
                "Accounting",
                format="html",
            )

        # 2. The move associated to the invoice have no lines. It is pointless -> break the link (set move_id to null)
        cr.execute(
            """
                UPDATE account_invoice SET move_id = NULL WHERE id IN (
                       SELECT invoice.id
                         FROM account_invoice invoice
                         JOIN account_move move ON move.id = invoice.move_id
                    LEFT JOIN account_move_line move_line ON move_line.move_id = move.id
                        WHERE invoice.state in ('draft', 'cancel')
                          AND invoice.move_id IS NOT NULL
                     GROUP BY invoice.id, move.id HAVING SUM(COALESCE(move_line.debit, 0)) = 0
                )
                RETURNING id, number, date_invoice
            """
        )
        unlink_because_empty = cr.fetchall()
        if unlink_because_empty:
            inconsistent_invoice_ids -= set([r[0] for r in unlink_because_empty])
            util.add_to_migration_reports(
                f"""
                    <details>
                    <summary>
                        {len(unlink_because_empty)} draft and cancelled invoices were linked to empty accounting
                        entries, which is inconsistent. To be able to upgrade properly, the links between the invoices
                        and their entry have been removed.
                        The moves, even if empty, have been kept, for history purposes.
                    </summary>
                    Invoices: {", ".join(f"{number}({date})" for _, number, date in unlink_because_empty)}
                    </details>
                """,
                "Accounting",
                format="html",
            )

        if inconsistent_invoice_ids:
            raise util.MigrationError(
                "%s invoices are in 'draft' or 'cancelled' state in pre-migration database, "
                "yet they are linked to an account.move. This is inconsistent and could come from an old bug or "
                "customization. Please investigate and fix it in pre-migration db. Invoice ids: (%s)"
                % (len(inconsistent_invoice_ids), ", ".join([str(r) for r in inconsistent_invoice_ids]))
            )

    cr.execute(
        """
        SELECT count(*), array_agg(id)
          FROM account_invoice
         WHERE state IN ('open', 'paid')
           AND move_id IS NULL
        """
    )
    invoices_count, invoices_ids = cr.fetchone()

    if invoices_count:
        ids = " Invoice ids: ({})".format(", ".join([str(r) for r in invoices_ids])) if invoices_count < 1000 else ""
        if not os.getenv("MIG_CREATE_MISSING_MOVES"):
            raise util.MigrationError(
                f"{invoices_count} invoices are in 'open' or 'paid' state"
                " but not linked to an account move in pre-migration database. "
                "Please investigate and fix it in pre-migration db. "
                "The configuration in the original database for the invoices is probably wrong"
                " and should preferably be corrected by customer."
                "It is possible to bypass this validation and automatically create draft invoices"
                " by setting the environment variable MIG_CREATE_MISSING_MOVES."
                f"Concerned {ids}"
            )
        else:
            # moves to be created in post-10-account-pocalypse.py
            util.add_to_migration_reports(
                "Account moves in draft created for some invoices %s", ", ".join([str(i) for i in invoices_ids]),
            )

    cr.execute(
        """
    UPDATE account_account a
       SET internal_type=t.type
      FROM account_account_type t
     WHERE a.user_type_id=t.id
       AND t.type!=a.internal_type
    """
    )

    cr.execute(
        """
    SELECT code
      FROM account_account
     WHERE internal_type in ('receivable', 'payable')
       AND reconcile = FALSE
    """
    )
    if cr.rowcount:
        faulty_accounts = ",".join([acc[0] for acc in cr.fetchall()])
        raise util.MigrationError(f"Accounts {faulty_accounts} are receivable/payable and not reconciliables.")
