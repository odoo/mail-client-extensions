# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.force_noupdate(cr, "sale_subscription.sale_subscription_stage_draft", False)
    util.force_noupdate(cr, "sale_subscription.sale_subscription_stage_in_progress", False)
    util.force_noupdate(cr, "sale_subscription.sale_subscription_stage_closed", False)
    # Migrate the account analytic tags
    if util.table_exists(cr, "account_analytic_tag_sale_order_rel"):
        cr.execute(
            """
            INSERT INTO account_analytic_tag_sale_order_rel(sale_order_id,account_analytic_tag_id)
                 SELECT sale_subscription_id,account_analytic_tag_id
                   FROM account_analytic_tag_sale_subscription_rel
            ON CONFLICT DO NOTHING
            """
        )

    model_ids = [
        (
            util.ref(cr, "sale.model_sale_order_line"),
            "new_sale_order_line_id",
            "sale_order_line",
            "sale_subscription_line",
        ),
        (
            util.ref(cr, "sale_management.model_sale_order_template"),
            "new_sale_order_template_id",
            "sale_order_template",
            "sale_subscription_template",
        ),
    ]
    for model_id, field, table, table_sub in model_ids:
        cr.execute(
            """
            SELECT f.name
              FROM ir_model_fields f
              JOIN information_schema.columns c1
                ON f.name = c1.column_name
               AND c1.table_name = %s
              JOIN information_schema.columns c2
                ON f.name = c2.column_name
               AND c2.table_name = %s
             WHERE f.model_id = %s
               AND f.state = 'manual'
               AND f.store = True
               AND f.ttype != 'binary'
            """,
            [table, table_sub, model_id],
        )
        info = cr.fetchall()
        columns = ",".join([f'"{column}" = {table_sub}."{column}"' for column, in info])
        if columns:
            query = f"""
                    UPDATE {table} t
                       SET {columns}
                      FROM {table_sub}
                     WHERE {table_sub}.{field} = t.id
                    """
            util.explode_execute(cr, query, table=table, alias="t")

    util.remove_model(cr, "sale.subscription.line", drop_table=False)

    cr.execute("DROP TABLE sale_subscription_template CASCADE")
    util.remove_column(cr, "sale_order_line", "old_subscription_line_id")
    util.remove_column(cr, "sale_order_line", "old_subscription_id")
    util.remove_column(cr, "sale_order_template", "old_template_id")
    util.remove_column(cr, "account_analytic_tag_sale_order_rel", "sale_subscription_id")
    util.remove_column(cr, "sale_order_starred_user_rel", "old_subscription_id")
    util.remove_column(cr, "sale_order_template_tag_rel", "old_template_id")
    util.remove_column(cr, "account_move_line", "old_subscription_id")
    util.remove_column(cr, "sale_temporal_recurrence", "sst_id")

    util.remove_view(cr, "sale_subscription.sale_subscription_view_list")
    util.remove_view(cr, "sale_subscription.sale_subscription_view_form")
    util.remove_view(cr, "sale_subscription.sale_subscription_view_pivot")
    util.remove_view(cr, "sale_subscription.sale_subscription_view_graph")
    util.remove_view(cr, "sale_subscription.sale_subscription_view_cohort")

    # arj todo: this query should be useless because the pricing_id is not required on the sol and the price_unit is
    # copied from the sale_subscription_line
    # util.parallel_execute(
    #     cr,
    #     util.explode_query_range(
    #         cr,
    #         """
    #      WITH sols as(
    #         SELECT sol.id as sol_id,
    #                pp.pricing_id
    #           FROM sale_order_line sol
    #           JOIN sale_order so ON sol.order_id = so.id
    #           JOIN product_product p ON p.id = sol.product_id
    #           JOIN product_template pt ON p.product_tmpl_id=pt.id
    #           LEFT JOIN LATERAL (
    #                 SELECT pp.id as pricing_id FROM product_pricing pp WHERE
    #                pp.recurrence_id = so.recurrence_id AND
    #                pp.product_template_id = p.product_tmpl_id AND
    #                pp.currency_id = sol.currency_id
    #                LIMIT 1
    #                ) AS pp ON TRUE
    #          WHERE so.state IN ('draft', 'sent')
    #            AND sol.pricing_id IS NULL
    #            AND pt.recurring_invoice
    #            AND so.is_subscription
    #            AND {parallel_filter}
    #      )
    #      UPDATE sale_order_line
    #         SET pricing_id = sols.pricing_id
    #        FROM sols
    #       WHERE sale_order_line.id = sols.sol_id
    #         """,
    #         table="sale_order_line",
    #         alias="sol",
    #     ),
    # )
    # results = cr.fetchall()
    # if results:
    #     # recompute pricing_id only when necessary
    #     sol_ids = [sol_id[0] for sol_id in results]
    #     util.recompute_fields(cr, "sale.order.line", ["pricing_id"], ids=sol_ids)

    cr.execute(
        "SELECT id FROM sale_order WHERE is_subscription=true AND old_subscription_id IS NOT NULL AND fiscal_position_id IS NULL"
    )
    util.recompute_fields(cr, "sale.order", ["fiscal_position_id"], ids=[so_id[0] for so_id in cr.fetchall()])

    cr.execute("SELECT id FROM sale_order WHERE currency_rate IS NULL")
    util.recompute_fields(cr, "sale.order", ["currency_rate"], ids=[id_ for id_, in cr.fetchall()])
    cr.execute(
        """
        SELECT sol.id
          FROM sale_order_line sol
          JOIN sale_order so ON so.id=sol.order_id
         WHERE so.is_subscription
           AND so.old_subscription_id IS NOT NULL
    """
    )
    sol_ids = [sol_id[0] for sol_id in cr.fetchall()]

    util.recompute_fields(cr, "sale.order.line", ["tax_id", "price_tax", "price_total"], ids=sol_ids, strategy="commit")

    cr.execute("SELECT id FROM sale_order WHERE is_subscription=true AND old_subscription_id IS NOT NULL")
    so_ids = [so_id[0] for so_id in cr.fetchall()]
    util.recompute_fields(cr, "sale.order", ["amount_total"], ids=so_ids)
    util.remove_column(cr, "sale_order", "old_subscription_id")

