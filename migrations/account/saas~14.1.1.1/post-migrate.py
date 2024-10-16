from odoo.upgrade import util


def migrate(cr, version):
    # ==========================================================================
    # Task 2363287 : Avoid tax tags inversion on aml
    # ==========================================================================

    # Set tax_tag_invert on all the move lines
    grids_refund_sql_conditions = [
        "account_move.tax_cash_basis_rec_id IS NULL AND account_move.move_type in ('in_refund', 'out_refund')",
    ]

    if util.module_installed(cr, "point_of_sale"):
        grids_refund_sql_conditions += [
            """(
                   EXISTS(SELECT id FROM pos_session WHERE pos_session.move_id = account_move.id)
                OR EXISTS(SELECT id FROM pos_order WHERE pos_order.account_move = account_move.id)
               )
               AND account_move.move_type = 'entry'
               AND account_move_line.debit > 0
            """,
        ]

    refund = " OR ".join(f"({cond})" for cond in grids_refund_sql_conditions)

    query = f"""
        UPDATE account_move_line
           SET tax_tag_invert = ((CASE WHEN account_move.tax_cash_basis_rec_id IS NULL AND account_journal.type = 'sale'
                                       THEN -1 ELSE 1 END
                                  * CASE WHEN {refund} THEN -1 ELSE 1 END)
                                = -1)
          FROM account_move, account_journal
         WHERE account_move.id = account_move_line.move_id
           AND account_journal.id = account_move_line.journal_id
           AND {{parallel_filter}}
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_move_line"))

    # Entries with taxes on misc entries might need to see their tag reinverted

    # Cash basis entries made from an invoice with some negative lines cannot be
    # reinverted with 100% certainty, so we don't reinvert them (this will not
    # impact the tax report, so it's okay). Their tags will stay explicitly inverted,
    # and they will have tax_tag_invert = False.
    # All the non-caba moves, as well as caba moves whose partial reconcile is not in this table
    # potentially need to be reinverted.
    cr.execute(
        """
        CREATE TABLE no_reinversion_caba_partial AS
            SELECT DISTINCT part.id
            FROM account_partial_reconcile part
            JOIN account_move_line aml
            ON aml.id = part.debit_move_id OR aml.id = part.credit_move_id
            WHERE EXISTS(
                SELECT inv_line.id
                FROM account_move_line inv_line
                JOIN account_move invoice
                ON invoice.id = inv_line.move_id
                WHERE invoice.move_type != 'entry'
                AND invoice.id = aml.move_id
                AND inv_line.quantity < 0
            )
    """
    )

    # Perform reinversion

    cr.execute(
        """
        CREATE TABLE amls_to_invert(
            id INTEGER NOT NULL UNIQUE
        )
    """
    )

    exclude_pos_entries = "TRUE"
    if util.module_installed(cr, "point_of_sale"):
        # Just like invoices, entries from POS shouldn't be reinverted (as they weren't inverted in the first place;
        # the tax report ran specific queries to guess the sign to apply on top of the tag and balance)
        exclude_pos_entries = """
            NOT EXISTS(SELECT id FROM pos_session WHERE pos_session.move_id = move.id)
            AND NOT EXISTS(SELECT id FROM pos_order WHERE pos_order.account_move = move.id)
        """

    cr.execute(
        f"""
        INSERT INTO amls_to_invert

            SELECT aml.id
            FROM account_move_line aml
            JOIN account_move move ON aml.move_id = move.id
            JOIN account_move_line_account_tax_rel aml_tx ON aml_tx.account_move_line_id = aml.id
            JOIN account_tax base_tax ON aml_tx.account_tax_id = base_tax.id
            LEFT JOIN no_reinversion_caba_partial ON move.tax_cash_basis_rec_id = no_reinversion_caba_partial.id
            WHERE
                no_reinversion_caba_partial.id IS NULL
                AND aml.tax_repartition_line_id IS NULL
                AND aml.credit > 0
                AND move.move_type = 'entry'
                AND {exclude_pos_entries}

            UNION

            SELECT aml.id
            FROM account_move_line aml
            JOIN account_move move ON aml.move_id = move.id
            JOIN account_tax_repartition_line tax_rep_ln ON tax_rep_ln.id = aml.tax_repartition_line_id
            JOIN account_tax tax_tax ON tax_tax.id = aml.tax_line_id
            LEFT JOIN no_reinversion_caba_partial ON move.tax_cash_basis_rec_id = no_reinversion_caba_partial.id
            WHERE
                no_reinversion_caba_partial.id IS NULL
                AND tax_tax.type_tax_use = 'sale'
                AND tax_rep_ln.invoice_tax_id IS NOT NULL
                AND move.move_type = 'entry'
                AND {exclude_pos_entries}

            UNION

            SELECT aml.id
            FROM account_move_line aml
            JOIN account_move move ON aml.move_id = move.id
            JOIN account_tax_repartition_line tax_rep_ln ON tax_rep_ln.id = aml.tax_repartition_line_id
            JOIN account_tax tax_tax ON tax_tax.id = aml.tax_line_id
            LEFT JOIN no_reinversion_caba_partial ON move.tax_cash_basis_rec_id = no_reinversion_caba_partial.id
            WHERE
                no_reinversion_caba_partial.id IS NULL
                AND tax_tax.type_tax_use = 'purchase'
                AND tax_rep_ln.refund_tax_id IS NOT NULL
                AND move.move_type = 'entry'
                AND {exclude_pos_entries}

        ON CONFLICT DO NOTHING
    """
    )

    query = """
        UPDATE account_move_line
           SET tax_tag_invert = NOT account_move_line.tax_tag_invert
          FROM amls_to_invert
         WHERE amls_to_invert.id = account_move_line.id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_move_line"))

    query = """
        UPDATE account_account_tag_account_move_line_rel rel
           SET account_account_tag_id = inverse_tag.id
          FROM account_account_tag inverse_tag, account_account_tag tag, amls_to_invert
         WHERE tag.id = rel.account_account_tag_id
           AND amls_to_invert.id = account_move_line_id
           AND SUBSTRING(inverse_tag.name, 2) = SUBSTRING(tag.name, 2)
           AND inverse_tag.country_id = tag.country_id
           AND inverse_tag.tax_negate = NOT tag.tax_negate
           AND NOT EXISTS (
                 SELECT 1
                   FROM account_account_tag_account_move_line_rel rel2
                  WHERE rel2.account_move_line_id = rel.account_move_line_id
                    AND rel2.account_account_tag_id = inverse_tag.id
                  LIMIT 1
           )
    """
    # TODO explode query?
    cr.execute(query)

    # cleanup
    cr.execute("DROP TABLE amls_to_invert")
    cr.execute("DROP TABLE no_reinversion_caba_partial")
