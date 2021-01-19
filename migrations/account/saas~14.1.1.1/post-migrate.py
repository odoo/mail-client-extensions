# -*- encoding: utf-8 -*-
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
    """
    util.parallel_execute(
        cr, util.explode_query_range(cr, query, table="account_move_line", prefix="account_move_line.")
    )

    # Entries with taxes on misc entries might need to see their tag reinverted

    # Cash basis entries made from an invoice with some negative lines cannot be
    # reinverted with 100% certainty, so we don't reinvert them (this will not
    # impact the tax report, so it's okay). Their tags will stay explicitly inverted,
    # and they will have tax_tag_invert = False.
    # All the non-caba moves, as well as caba moves whose partial reconcile is not in this table
    # potentially need to be reinverted.
    cr.execute("""
        CREATE TABLE no_reinversion_caba_partial AS
            SELECT DISTINCT part.id
            FROM account_move_line aml
            JOIN account_move invoice ON invoice.id = aml.move_id AND invoice.move_type != 'entry'
            JOIN account_partial_reconcile part ON aml.id = part.debit_move_id OR aml.id = part.credit_move_id
            JOIN account_move caba_move ON part.id = caba_move.tax_cash_basis_rec_id
            JOIN account_account_tag_account_move_line_rel aml_tags on aml_tags.account_move_line_id = aml.id
            WHERE aml.quantity < 0
    """)

    # Perform reinversion

    cr.execute("""
        CREATE TABLE amls_to_invert(
            id INTEGER NOT NULL UNIQUE
        )
    """)

    amls_to_invert_populate_queries = [
        """
            INSERT INTO amls_to_invert
                SELECT DISTINCT aml.id
                FROM account_move_line aml
                JOIN account_move move ON aml.move_id = move.id
                JOIN account_move_line_account_tax_rel aml_tx ON aml_tx.account_move_line_id = aml.id
                JOIN account_tax base_tax ON aml_tx.account_tax_id = base_tax.id
                LEFT JOIN no_reinversion_caba_partial ON move.tax_cash_basis_rec_id = no_reinversion_caba_partial.id
                WHERE
                    no_reinversion_caba_partial.id IS NULL
                    AND aml.tax_repartition_line_id IS NULL
                    AND aml.credit > 0
            ON CONFLICT DO NOTHING
        """,
        """
            INSERT INTO amls_to_invert
                SELECT DISTINCT aml.id
                FROM account_move_line aml
                JOIN account_move move ON aml.move_id = move.id
                JOIN account_tax_repartition_line tax_rep_ln ON tax_rep_ln.id = aml.tax_repartition_line_id
                JOIN account_tax tax_tax ON tax_tax.id = aml.tax_line_id
                LEFT JOIN no_reinversion_caba_partial ON move.tax_cash_basis_rec_id = no_reinversion_caba_partial.id
                WHERE
                    no_reinversion_caba_partial.id IS NULL
                    AND tax_tax.type_tax_use = 'sale'
                    AND tax_rep_ln.invoice_tax_id IS NOT NULL
            ON CONFLICT DO NOTHING
        """,
        """
            INSERT INTO amls_to_invert
                SELECT DISTINCT aml.id
                FROM account_move_line aml
                JOIN account_move move ON aml.move_id = move.id
                JOIN account_tax_repartition_line tax_rep_ln ON tax_rep_ln.id = aml.tax_repartition_line_id
                JOIN account_tax tax_tax ON tax_tax.id = aml.tax_line_id
                LEFT JOIN no_reinversion_caba_partial ON move.tax_cash_basis_rec_id = no_reinversion_caba_partial.id
                WHERE
                    no_reinversion_caba_partial.id IS NULL
                    AND tax_tax.type_tax_use = 'purchase'
                    AND tax_rep_ln.refund_tax_id IS NOT NULL
            ON CONFLICT DO NOTHING
        """,
        """
            INSERT INTO amls_to_invert
                SELECT DISTINCT aml.id
                FROM account_move_line aml
                JOIN account_move move ON aml.move_id = move.id
                LEFT JOIN no_reinversion_caba_partial ON move.tax_cash_basis_rec_id = no_reinversion_caba_partial.id
                WHERE
                    no_reinversion_caba_partial.id IS NULL
                    AND NOT EXISTS(
                        SELECT account_tax_id
                        FROM account_move_line_account_tax_rel
                        WHERE account_move_line_id = aml.id
                    )
                    AND EXISTS(
                        SELECT account_account_tag_id
                        FROM account_account_tag_account_move_line_rel aml_tags
                        WHERE aml_tags.account_move_line_id = aml.id
                    )
                    AND aml.tax_repartition_line_id IS NULL
                    AND move.move_type IN ('out_invoice', 'out_receipt', 'in_refund')
            ON CONFLICT DO NOTHING
        """,
    ]

    util.parallel_execute(cr, amls_to_invert_populate_queries)

    query = """
        UPDATE account_move_line
           SET tax_tag_invert = NOT account_move_line.tax_tag_invert
          FROM amls_to_invert
         WHERE amls_to_invert.id = account_move_line.id
    """
    util.parallel_execute(
        cr, util.explode_query_range(cr, query, table="account_move_line", prefix="account_move_line.")
    )

    query = """
        UPDATE account_account_tag_account_move_line_rel rel
           SET account_account_tag_id = inverse_tag.id
          FROM account_account_tag inverse_tag, account_account_tag tag, amls_to_invert
         WHERE tag.id = rel.account_account_tag_id
           AND amls_to_invert.id = account_move_line_id
           AND SUBSTRING(inverse_tag.name, 2) = SUBSTRING(tag.name, 2)
           AND inverse_tag.country_id = tag.country_id
           AND inverse_tag.tax_negate = NOT tag.tax_negate
    """
    # TODO explode query?
    cr.execute(query)

    # cleanup
    cr.execute("DROP TABLE amls_to_invert")
    cr.execute("DROP TABLE no_reinversion_caba_partial")
