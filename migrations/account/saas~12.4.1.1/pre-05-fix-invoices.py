# -*- encoding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Some debit notes (=credit note of a credit note) were encoded as refund
    # invoices in the past, while their account.move corresponded to an invoice.
    # This causes the sign of their total amount to be inverted in v13. To avoid that,
    # we fix their type in pre.
    cr.execute(
        """
        UPDATE account_invoice inv
           SET type = CASE WHEN inv.type = 'out_refund' THEN 'out_invoice' ELSE 'in_invoice' END
          FROM account_move_line aml, account_move move
         WHERE move.id = aml.move_id
           AND inv.move_id = move.id
           AND inv.account_id = aml.account_id
           AND ((inv.type = 'out_refund' AND aml.debit > 0)
                OR (inv.type = 'in_refund' AND aml.credit > 0))
           AND inv.amount_untaxed > 0 -- we want to keep negative invoices, even if they are not allowed anymore
    """
    )

    # Some draft or cancelled invoices might reference taxes from other companies
    # (not supposed to happen, but it happens). This had no consequence before
    # saas-12.4, but it crashes during the migration process to 12.4, when
    # trying to migrate the taxes made on the journal items that were generated for
    # those invoices. Hence, we need to fix this inconsistency; this is done by
    # simply removing those taxes from the invoice lines.
    cr.execute(
        """
        SELECT invltx.invoice_line_id, invltx.tax_id
          FROM account_invoice_line_tax invltx
          JOIN account_tax tax ON invltx.tax_id = tax.id
          JOIN account_invoice_line invl ON invl.id = invltx.invoice_line_id
          JOIN account_invoice inv ON inv.id = invl.invoice_id
         WHERE inv.state IN ('draft', 'cancel')
           AND tax.company_id != inv.company_id;
    """
    )

    wrong_invltx_data = cr.fetchall()

    if wrong_invltx_data:
        cr.execute(
            """
            DELETE FROM account_invoice_line_tax
                  WHERE (invoice_line_id, tax_id) IN %(invltx_vals)s;
        """,
            {"invltx_vals": tuple(wrong_invltx_data)},
        )

        wrong_inv_count = len(wrong_invltx_data)
        util.add_to_migration_reports(
            f"{wrong_inv_count} draft of cancelled invoices referenced taxes from another company. "
            "These inconsistent taxes have been removed from those invoices.",
            "Accounting",
        )
