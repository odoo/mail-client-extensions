# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sale_subscription", "campaign_id", "integer")
    util.create_column(cr, "sale_subscription", "source_id", "integer")
    util.create_column(cr, "sale_subscription", "medium_id", "integer")

    cr.execute(
        """
            UPDATE sale_subscription
               SET campaign_id = so.campaign_id,
                   source_id = so.source_id,
                   medium_id = so.medium_id
              FROM sale_order_line sol
              JOIN sale_order so ON sol.order_id = so.id
             WHERE sale_subscription.id = sol.subscription_id
        """
    )
