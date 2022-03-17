# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sale_subscription", "campaign_id", "integer")
    util.create_column(cr, "sale_subscription", "source_id", "integer")
    util.create_column(cr, "sale_subscription", "medium_id", "integer")

    query = """
            UPDATE sale_subscription sub
               SET campaign_id = so.campaign_id,
                   source_id = so.source_id,
                   medium_id = so.medium_id
              FROM sale_order_line sol
              JOIN sale_order so ON sol.order_id = so.id
             WHERE sub.id = sol.subscription_id
        """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="sale_subscription", alias="sub"))
