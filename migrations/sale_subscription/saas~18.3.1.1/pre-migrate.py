from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sale_order", "is_closing", "boolean", default=False)

    query = """
        UPDATE sale_order so
           SET is_closing = TRUE
          FROM sale_subscription_plan sp
         WHERE so.plan_id = sp.id
           AND so.subscription_state IN ('3_progress', '4_paused')
           AND sp.user_closable = TRUE
           AND so.end_date IS NOT NULL
           AND so.next_invoice_date IS NOT NULL
           AND so.end_date <= so.next_invoice_date
    """
    util.explode_execute(cr, query, table="sale_order", alias="so")

    util.explode_execute(
        cr,
        """
        UPDATE sale_order_line sol
           SET display_type = 'subscription_discount'
          FROM sale_order so
         WHERE sol.order_id = so.id
           AND so.subscription_state = '7_upsell'
           AND sol.display_type = 'line_note'
           AND sol.name LIKE '(*)%'
        """,
        table="sale_order_line",
        alias="sol",
    )
    util.remove_view(cr, "sale_subscription.view_quotation_tree_subscription")

    util.remove_record(cr, "sale_subscription.module_category_subscription_management")
