# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.alter_column_type(
        cr, "account_report", "filter_account_type", "varchar", using="CASE WHEN {0} THEN 'both' ELSE 'disabled' END"
    )
    util.remove_view(cr, "account.view_account_analytic_line_filter_inherit")

    cr.execute("DROP INDEX IF EXISTS account_move_line__unreconciled_index")
    cr.execute(
        """
        CREATE INDEX "account_move_line__unreconciled_index"
                  ON "account_move_line"
               USING btree (account_id, partner_id)
                  -- Match exactly how the ORM converts domains to ensure the query planner uses it
               WHERE (reconciled IS NULL OR reconciled = false OR reconciled IS NOT true) AND parent_state = 'posted'
    """
    )

    util.convert_field_to_translatable(cr, "account.reconcile.model.line", "label")

    cr.execute(
        """
        CREATE TABLE duplicates AS
        SELECT name,
               applicability,
               country_id,
               ARRAY_AGG(id ORDER BY active DESC, id) AS ids
          FROM account_account_tag
      GROUP BY name, applicability, country_id
        HAVING COUNT(*) > 1
        """
    )

    to_update = (
        ("account_account_account_tag", "account_account", "account_account_id"),
        ("account_account_tag_product_template_rel", "product_template", "product_template_id"),
        (
            "account_account_tag_account_tax_repartition_line_rel",
            "account_tax_repartition_line",
            "account_tax_repartition_line_id",
        ),
        ("account_account_tag_account_move_line_rel", "account_move_line", "account_move_line_id"),
    )
    queries = []
    for table, ftable, fcolumn in to_update:
        queries.extend(
            util.explode_query_range(
                cr,
                f"""
                UPDATE {table} t
                   SET account_account_tag_id = dm.ids[1]
                  FROM duplicates AS dm,
                       {ftable} t2
                 WHERE t.account_account_tag_id = ANY(dm.ids[2:])
                   AND t.{fcolumn} = t2.id
                """,
                table=ftable,
                alias="t2",
            )
        )
    util.parallel_execute(cr, queries)

    cr.execute(
        """
        DELETE FROM account_account_tag t
         USING duplicates dm
         WHERE t.id = ANY(dm.ids[2:]);

          DROP TABLE duplicates;
        """
    )

    util.remove_field(cr, "account.full.reconcile", "name")
    util.delete_unused(cr, "account.sequence_reconcile_seq")

    util.explode_execute(
        cr,
        """
        UPDATE account_move_line
           SET matching_number = full_reconcile_id::varchar
         WHERE full_reconcile_id IS NOT NULL
        """,
        table="account_move_line",
    )

    util.explode_execute(
        cr,
        """
            WITH RECURSIVE partials (line_id, current_id) AS (
                    SELECT line.id,
                           line.id
                      FROM account_move_line line
                      JOIN account_partial_reconcile partial
                        ON line.id = partial.debit_move_id
                        OR line.id = partial.credit_move_id
                     WHERE line.full_reconcile_id IS NULL
                       AND {parallel_filter}
                                                UNION
                    SELECT p.line_id,
                           CASE WHEN partial.debit_move_id = p.current_id THEN partial.credit_move_id
                                ELSE partial.debit_move_id
                           END
                      FROM partials p
                      JOIN account_partial_reconcile partial ON p.current_id = partial.debit_move_id
                                                             OR p.current_id = partial.credit_move_id
            ), new_vals AS (
                  SELECT line_id, 'P' || MIN(partial.id) AS matching_number
                    FROM partials
                    JOIN account_partial_reconcile partial ON current_id = partial.debit_move_id
                                                           OR current_id = partial.credit_move_id
                GROUP BY line_id
            )
            UPDATE account_move_line line
               SET matching_number = new_vals.matching_number
              FROM new_vals
             WHERE new_vals.line_id = line.id
        """,
        table="account_move_line",
        alias="line",
    )
