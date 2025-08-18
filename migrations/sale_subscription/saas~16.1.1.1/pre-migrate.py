from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("DROP VIEW IF EXISTS sale_subscription_report CASCADE")
    util.change_field_selection_values(cr, "sale.order.alert", "action", {"email": "mail_post"})

    # First order of a sequence should have an empty origin_order_id
    # Duplicated orders should not share the same origin_order_id if they are not renew or upsell
    query = """
        UPDATE sale_order so
           SET origin_order_id = null
         WHERE so.is_subscription = true
           AND COALESCE(so.subscription_management, '') NOT IN ('renew', 'upsell')
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="sale_order", alias="so"))

    util.create_column(cr, "sale_order", "first_contract_date", "date")
    util.explode_execute(
        cr,
        """
        WITH info AS (
            SELECT o.id,
                   CASE o.subscription_management
                       WHEN 'renew' THEN oo.start_date
                       WHEN 'upsell' THEN oo.start_date
                       ELSE o.start_date
                   END AS start_date
              FROM sale_order o
         LEFT JOIN sale_order oo
                ON o.origin_order_id = oo.id
             WHERE o.is_subscription
               AND {parallel_filter}
        )
        UPDATE sale_order o
           SET first_contract_date = info.start_date
          FROM info
         WHERE o.id = info.id
        """,
        table="sale_order",
        alias="o",
    )
