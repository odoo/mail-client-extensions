from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_mx_edi.view_out_invoice_tree_inherit_l10n_mx_edi")
    util.remove_view(cr, "l10n_mx_edi.view_out_credit_note_tree_inherit_l10n_mx_edi")
    util.remove_view(cr, "l10n_mx_edi.view_in_invoice_bill_tree_inherit_l10n_mx_edi")
    util.remove_view(cr, "l10n_mx_edi.view_in_invoice_refund_tree_inherit_l10n_mx_edi")

    ## Pre-compute stored computed field `l10n_mx_edi_payment_policy`
    util.create_column(cr, "account_move", "l10n_mx_edi_payment_policy", "varchar")

    # Get payment terms with at least 2 payment term lines
    cr.execute(
        """
         SELECT payment_id AS id
           FROM account_payment_term_line
       GROUP BY payment_id
         HAVING COUNT(*) > 1
        """
    )
    ppd_payment_term_ids = tuple(_id for (_id,) in cr.fetchall())

    # Set `l10n_mx_edi_payment_policy` in DB
    query = cr.mogrify(
        """
        UPDATE account_move move
           SET l10n_mx_edi_payment_policy = CASE WHEN move.move_type = 'out_invoice'
                                                  AND move.invoice_date_due > move.invoice_date
                                                  AND (
                                                       -- due date after the last day of the month of the invoice date
                                                       date_trunc('month', move.invoice_date_due) > move.invoice_date
                                                       OR move.invoice_payment_term_id IN %s
                                                  )
                                                  THEN 'PPD'
                                                  ELSE 'PUE'
                                            END
         WHERE move.l10n_mx_edi_is_cfdi_needed
           AND move.move_type != 'entry'  -- equivalent to move.is_invoice(include_receipts=True)
           AND move.invoice_date_due IS NOT NULL
           AND move.invoice_date IS NOT NULL
           AND {parallel_filter}
        """,
        [ppd_payment_term_ids],
    ).decode()
    util.explode_execute(cr, query, table="account_move", alias="move")
