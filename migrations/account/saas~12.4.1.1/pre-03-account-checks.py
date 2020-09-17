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
        # Try to fix the inconsistencies automatically

        # 1. The move associated to the invoice have no lines. It is pointless -> break the link (set move_id to null)
        inconsistent_invoice_ids = set(inconsistent_invoice_ids)
        cr.execute(
            """
                UPDATE account_invoice SET move_id = NULL WHERE id IN (
                       SELECT invoice.id
                         FROM account_invoice invoice
                         JOIN account_move move ON move.id = invoice.move_id
                    LEFT JOIN account_move_line move_line ON move_line.move_id = move.id
                        WHERE invoice.state in ('draft', 'cancel')
                          AND invoice.move_id IS NOT NULL
                     GROUP BY invoice.id, move.id HAVING COUNT(move_line.id) = 0
                )
                RETURNING id
            """
        )
        unlink_because_empty = [r[0] for r in cr.fetchall()]
        if unlink_because_empty:
            inconsistent_invoice_ids -= set(unlink_because_empty)
            util.add_to_migration_reports(
                f"""
                    <details>
                    <summary>
                        {len(unlink_because_empty)} draft and cancelled invoices were linked to empty accounting
                        entries, which is inconsistent. To be able to upgrade properly, the links between the invoices
                        and their entry have been removed.
                        The moves, even if empty, have been kept, for history purposes.
                    </summary>
                    Invoice ids: {unlink_because_empty}
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
