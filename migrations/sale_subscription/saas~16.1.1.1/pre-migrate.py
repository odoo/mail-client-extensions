# -*- coding: utf-8 -*-

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
