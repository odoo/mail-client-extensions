# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sale_subscription_pricing", "active", "boolean", default=True)

    cr.execute(
        """
        UPDATE sale_subscription_pricing sub_pricing
           SET active = False
          FROM product_pricelist pricelist
         WHERE sub_pricing.pricelist_id = pricelist.id
           AND pricelist.active IS NOT True
    """
    )

    # Having a recurring bill of 0 doesn't make sense
    cr.execute(
        """
           UPDATE sale_subscription_plan
              SET billing_period_value = 1
            WHERE billing_period_value <= 0
        RETURNING id, name->>'en_US'
        """
    )

    if cr.rowcount > 0:
        subs_recurring_period = "\n".join(
            "<li>{}</li>".format(util.get_anchor_link_to_record("sale.subscription.plan", _id, name))
            for _id, name in cr.fetchall()
        )
        util.add_to_migration_reports(
            message=f"""
            <details>
              <summary>
                The billing period of Sale Subscription plans must be a positive quantity.
                We have reset the following recurring plans to have a billing period of 1.
              </summary>
              <ul>
                {subs_recurring_period}
              </ul>
            </details>
            """,
            format="html",
            category="Subscription",
        )
