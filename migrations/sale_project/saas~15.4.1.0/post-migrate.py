# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    if not util.env(cr).user.has_group("project.group_project_milestone"):
        cr.execute(
            """
            UPDATE product_template
               SET service_type = 'manual'
             WHERE type = 'service'
               AND invoice_policy = 'delivery'
               AND service_type = 'milestones'
         RETURNING id
            """
        )
        product_template_ids = tuple((res[0] for res in cr.fetchall()))
        if product_template_ids:
            query = cr.mogrify(
                """
                    UPDATE sale_order_line l
                       SET qty_delivered_method = 'manual'
                      FROM product_product p
                     WHERE p.id = l.product_id
                       AND p.product_tmpl_id IN %s
                """,
                [product_template_ids],
            ).decode()
            util.parallel_execute(cr, util.explode_query_range(cr, query, table="sale_order_line", alias="l"))
