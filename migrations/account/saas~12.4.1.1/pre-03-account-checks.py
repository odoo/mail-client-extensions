# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT count(*), array_agg(id)
          FROM account_invoice
         WHERE state IN ('draft', 'cancel')
           AND move_id IS NOT NULL
    """
    )
    inconsistent_invoices_count, invoices_ids = cr.fetchone()
    if inconsistent_invoices_count:
        raise util.MigrationError(
            "%s invoices are in 'draft' or 'cancelled' state in pre-migration database, "
            "yet they are linked to an account.move. This is inconsistent and could come from an old bug or "
            "customization. Please investigate and fix it in pre-migration db. Invoice ids: (%s)"
            % (inconsistent_invoices_count, ", ".join([str(r) for r in invoices_ids]))
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

        raise util.MigrationError(
            "%s invoices are in 'open' or 'paid' state but not linked to an account move in pre-migration database. "
            "Please investigate and fix it in pre-migration db.%s" % (invoices_count, ids)
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
