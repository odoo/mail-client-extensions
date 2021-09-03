# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "product_template_attribute_line", "value_count", "int4", default=0)

    cr.execute(
        """
        WITH attcount AS (
            SELECT product_template_attribute_line_id as id, count(*) as count
              FROM product_attribute_value_product_template_attribute_line_rel
          GROUP BY product_template_attribute_line_id
        )
        UPDATE product_template_attribute_line ptal
           SET value_count = a.count
          FROM attcount a
         WHERE a.id = ptal.id
    """
    )
