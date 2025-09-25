from odoo.upgrade import util


def migrate(cr, version):
    # delivery could be freshly installed
    if util.table_exists(cr, "delivery_price_rule"):
        _migrate_delivery_price_rule(cr)


def _migrate_delivery_price_rule(cr):
    cr.execute(
        """
        WITH updated AS (
            UPDATE delivery_price_rule
               SET sequence = delivery_price_rule.sequence + 10
              FROM delivery_carrier dc
             WHERE delivery_price_rule.carrier_id = dc.id
               AND dc.delivery_type = 'base_on_rule'
               AND dc.free_over
               AND dc.amount > 0.00
         RETURNING dc.id, dc.name
        )
        SELECT DISTINCT ON (id) id, name->>'en_US' FROM updated
        """
    )
    carrier = cr.fetchall()
    if carrier:
        cr.execute(
            """
            INSERT INTO delivery_price_rule
                        (sequence, carrier_id, variable, operator,
                        max_value, list_base_price, list_price, variable_factor)
                 SELECT 1, id, 'price', '>=',
                        amount, 0.0, 0.0, 'weight'
                   FROM delivery_carrier
                  WHERE id IN %s
            """,
            [tuple(id[0] for id in carrier)],
        )
        util.add_to_migration_reports(
            category="Delivery",
            message=(
                """
                <details>
                    <summary>
                        Some shipping methods using the "Based on Rules" provider also have
                        the "Free delivery for orders above a specified amount" option set.
                        Since Odoo 17 the free delivery option is ignored for
                        shipping methods based on rules.
                        To keep the same behavior, a new Pricing Rule has been
                        automatically created that ensures free delivery functionality
                        for eligible orders.
                        Please take a moment to review the affected shipping methods listed below.
                        If you notice any inconsistency, feel free to adjust the Pricing rules or
                        free delivery settings in your database and submit a new upgrade request.
                    </summary>
                    <ul>{}</ul>
                </details>
                """.format(
                    " ".join(
                        f"<li>{util.get_anchor_link_to_record('delivery.carrier', id, name)}</li>"
                        for id, name in carrier
                    )
                )
            ),
            format="html",
        )
