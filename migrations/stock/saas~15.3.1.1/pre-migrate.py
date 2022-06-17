# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "stock_move_line", "product_category_name", "varchar")

    query = """
        UPDATE stock_move_line l
           SET product_category_name = c.complete_name
          FROM product_product p
          JOIN product_template pt ON p.product_tmpl_id = pt.id
          JOIN product_category c ON pt.categ_id = c.id
         WHERE l.product_id = p.id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="stock_move_line", alias="l"))
