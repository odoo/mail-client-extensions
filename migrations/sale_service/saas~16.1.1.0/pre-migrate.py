# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "sale_project"):
        util.move_field_to_module(cr, "sale.order.line", "is_service", "sale_project", "sale_service")
    else:
        util.create_column(cr, "sale_order_line", "is_service", "boolean", default=False)
        query = """
            UPDATE sale_order_line l
               SET is_service = true
              FROM product_product p
              JOIN product_template t
                ON t.id = p.product_tmpl_id
             WHERE p.id = l.product_id
               AND t.type = 'service'
        """
        util.parallel_execute(cr, util.explode_query_range(cr, query, table="sale_order_line", alias="l"))
