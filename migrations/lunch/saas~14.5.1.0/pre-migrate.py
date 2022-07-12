# -*- coding: utf-8 -*-

import itertools

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "lunch.product.report")

    util.create_column(cr, "lunch_order", "name", "varchar")
    query = """
        UPDATE lunch_order lo
           SET name = product.name
          FROM lunch_product product
         WHERE lo.product_id = product.id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="lunch_order", alias="lo"))

    util.create_column(cr, "lunch_order", "lunch_location_id", "int4")
    query = """
        UPDATE lunch_order lo
           SET lunch_location_id = u.last_lunch_location_id
          FROM res_users u
         WHERE lo.user_id = u.id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="lunch_order", alias="lo"))

    # Duplicate toppings used by multiple suppliers
    columns = util.get_columns(cr, "lunch_topping", ("id",))
    columns_pre = [f"t.{c}" for c in columns]

    util.create_column(cr, "lunch_topping", "supplier_id", "int4")

    cr.execute(
        f"""
            WITH suppliers_per_category AS (
                SELECT p.category_id,
                       min(p.supplier_id) as sup_id,
                       (array_agg(DISTINCT p.supplier_id ORDER BY p.supplier_id))[2:] sup_ids
                  FROM lunch_product p
                  JOIN lunch_topping t USING (category_id)
                 WHERE p.category_id IS NOT NULL
                   AND p.supplier_id IS NOT NULL
              GROUP BY p.category_id
            ),
            _udpate AS (
                UPDATE lunch_topping t
                   SET supplier_id = s.sup_id
                  FROM suppliers_per_category s
                 WHERE s.category_id = t.category_id
            )
            INSERT INTO lunch_topping({','.join(columns)}, supplier_id)
            SELECT {','.join(columns_pre)}, unnest(s.sup_ids) supplier_id
              FROM lunch_topping t
              JOIN suppliers_per_category s USING (category_id)
        """
    )

    # Now, copy the labels and quantities from the most used category on suppliers
    util.create_column(cr, "lunch_supplier", "topping_label_1", "varchar", default="Extras")
    util.create_column(cr, "lunch_supplier", "topping_label_2", "varchar", default="Beverages")
    util.create_column(cr, "lunch_supplier", "topping_label_3", "varchar", default="Extra Label 3")

    util.create_column(cr, "lunch_supplier", "topping_quantity_1", "varchar", default="0_more")
    util.create_column(cr, "lunch_supplier", "topping_quantity_2", "varchar", default="0_more")
    util.create_column(cr, "lunch_supplier", "topping_quantity_3", "varchar", default="0_more")

    cr.execute(
        """
            WITH counts AS (
                SELECT supplier_id, category_id, count(*) as nbr
                  FROM lunch_topping
                 WHERE supplier_id IS NOT NULL
                   AND category_id IS NOT NULL
              GROUP BY supplier_id, category_id
            ),
            ordered AS (
                SELECT supplier_id, category_id, row_number() OVER(PARTITION BY supplier_id ORDER BY nbr DESC) as rank
                  FROM counts
            ),
            most_used_category AS (
                SELECT supplier_id, category_id
                  FROM ordered
                 WHERE rank = 1
            )

            UPDATE lunch_supplier s
               SET topping_label_1 = c.topping_label_1,
                   topping_label_2 = c.topping_label_2,
                   topping_label_3 = c.topping_label_3,
                   topping_quantity_1 = c.topping_quantity_1,
                   topping_quantity_2 = c.topping_quantity_2,
                   topping_quantity_3 = c.topping_quantity_3
              FROM most_used_category m
              JOIN lunch_product_category c ON c.id = m.category_id
             WHERE m.supplier_id = s.id

        """
    )

    # Fields cleanup
    util.remove_field(cr, "lunch.topping", "category_id")

    for name, index in itertools.product(["label", "quantity", "ids"], ["1", "2", "3"]):
        util.remove_field(cr, "lunch.product.category", f"topping_{name}_{index}")
