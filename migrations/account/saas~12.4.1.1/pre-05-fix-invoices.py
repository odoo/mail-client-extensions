# -*- encoding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Some debit notes (=credit note of a credit note) were encoded as refund
    # invoices in the past, while their account.move corresponded to an invoice.
    # This causes the sign of their total amount to be inverted in v13. To avoid that,
    # we fix their type in pre.
    cr.execute(
        """
        WITH move_line_sum_by_account AS (
            SELECT move_id, account_id, sum(balance) as balance_sum
              FROM account_move_line
          GROUP BY move_id, account_id
        )
        UPDATE account_invoice inv
           SET type = CASE WHEN inv.type = 'out_refund' THEN 'out_invoice' ELSE 'in_invoice' END
          FROM move_line_sum_by_account aml_sum, account_move move
         WHERE move.id = aml_sum.move_id
           AND inv.move_id = move.id
           AND inv.account_id = aml_sum.account_id
           AND ((inv.type = 'out_refund' AND aml_sum.balance_sum > 0)
                OR (inv.type = 'in_refund' AND aml_sum.balance_sum < 0))
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
        DELETE FROM account_invoice_line_tax lt
              USING account_tax t,
                    account_invoice_line l,
                    account_invoice i
              WHERE t.id = lt.tax_id
                AND l.id = lt.invoice_line_id
                AND i.id = l.invoice_id
                AND i.state IN ('draft', 'cancel')
                AND t.company_id != i.company_id
        """
    )
    wrong_inv_count = cr.rowcount
    if wrong_inv_count:
        util.add_to_migration_reports(
            f"{wrong_inv_count} draft of cancelled invoices referenced taxes from another company. "
            "These inconsistent taxes have been removed from those invoices.",
            "Accounting",
        )
