from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "sale.order", "archived_product_ids")
    util.remove_field(cr, "sale.order", "archived_product_count")
    cr.execute(
        """
        UPDATE sale_order
           SET subscription_state =
               CASE
                   WHEN subscription_id IS NULL THEN '1_draft'
                   ELSE '2_renewal'
               END
         WHERE is_subscription = TRUE
           AND state IN ('draft', 'sent')
           AND subscription_state IN ('3_progress', '4_paused')
     RETURNING id, name
        """
    )
    sub_ids = cr.fetchall()
    if sub_ids:
        util.add_to_migration_reports(
            """
            <details>
                <summary>
                    The following subscriptions have been updated because you cannot have a draft SO be a confirmed subscription.
                </summary>
                <ul>{}</ul>
            </details>
            """.format(
                " ".join(f"<li>{util.get_anchor_link_to_record('sale.order', id, name)}</li>" for id, name in sub_ids)
            ),
            category="Subscription",
            format="html",
        )
