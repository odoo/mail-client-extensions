# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    """ In (really) old versions, it was possible (while not 100% correct) to use an
    account that wasn't payable nor receivable on invoices (only reconcilable).
    Those accounts should have been payable/receivable, and fixing is required
    for 12.4 invoices to work properly. In this script, we search for those accounts
    and fix their type with respect to the invoice types they were used with.
    """
    env = util.env(cr)
    receivable_type = env.ref("account.data_account_type_receivable")
    payable_type = env.ref("account.data_account_type_payable")

    cr.execute(
        """
        SELECT acc.id as account_id, inv.type as invoice_type
          FROM account_move_line aml
          JOIN account_account acc ON acc.id = aml.account_id
          JOIN account_invoice inv ON inv.move_id = aml.move_id
         WHERE aml.account_internal_type NOT IN ('receivable', 'payable')
           AND inv.account_id = aml.account_id
      GROUP BY acc.id, inv.type
    """
    )

    res = cr.dictfetchall()

    already_treated = {"in": set(), "ou": set()}  # We keep 'in' and 'ou' as keys, to regroup invoices and refunds
    for account_id, invoice_type in cr.fetchall():
        doc_type_key = invoice_type[:2]

        if account_id in already_treated[doc_type_key]:
            # Should never happen ... normally. It wouldn't make sense; an account can't be both payable and receivable
            raise util.MigrationError(f"Account with id {account_id} is used on both sale and purchase documents.")

        account = env["account.account"].browse(account_id)

        if doc_type_key == "in":
            account.write({"user_type_id": payable_type.id})
        elif doc_type_key == "ou":
            account.write({"user_type_id": receivable_type.id})
        else:
            raise util.MigrationError(f"Unknown invoice type: {doc_type_key}")

        already_treated[doc_type_key].add(account_id)

    # Now, we need to ensure that the move lines made on those accounts have
    # exclude_from_invoice_tab = True, so that the migration can go on smoothly
    all_treated_accounts = already_treated["in"] | already_treated["ou"]
    if all_treated_accounts:
        cr.execute(
            """
            UPDATE account_move_line
               SET exclude_from_invoice_tab = true
             WHERE account_id in %s
        """,
            [tuple(all_treated_accounts)],
        )
