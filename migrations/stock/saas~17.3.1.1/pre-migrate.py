from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "stock_move_line", "product_category_name")
    util.remove_column(cr, "stock_warehouse_orderpoint", "qty_to_order")
    util.remove_field(cr, "res.config.settings", "group_stock_storage_categories")
    util.remove_record(cr, "stock.group_stock_storage_categories")
    util.remove_record(cr, "stock.menu_reordering_rules_config")
    util.create_column(cr, "stock_putaway_rule", "sublocation", "varchar", default="no")

    # Putaway sublocation strategy will be set to 'closest location
    # for rules having storage category set
    query = """
        UPDATE stock_putaway_rule
           SET sublocation = 'closest_location'
         WHERE storage_category_id IS NOT NULL
    """
    cr.execute(query)

    util.create_column(cr, "product_template", "is_storable", "boolean")
    util.explode_execute(
        cr,
        """
        UPDATE product_template
           SET is_storable = TRUE
         WHERE type = 'product'
        """,
        table="product_template",
    )

    def adapter_product(leaf, _or, _neg):
        # Adapt the selection value 'product' in `product.template.type`
        # into `is_storable` boolean field. Since not all leaves need to be adapted
        # we need to replace the left path manually.
        left, op, right = leaf
        path = left.split(".")
        path[-1] = "is_storable"
        new_left = ".".join(path)
        if right == "product" and op in ("=", "!="):
            return [(new_left, "=", op == "=")]
        elif right == "consu" and op == "=":
            return ["&", leaf, (new_left, "=", False)]
        elif right == "consu" and op == "!=":
            return ["|", leaf, "&", (left, "=", right), (new_left, "=", True)]
        elif isinstance(right, (tuple, list)) and "product" in right and op in ("in", "not in"):
            new_right = list(right)
            new_right.remove("product")
            if not new_right:
                return [(new_left, "=", op == "in")]
            return ["|" if op == "in" else "&", (new_left, "=", op == "in"), (left, op, new_right)]
        elif isinstance(right, (tuple, list)) and "consu" in right and op in ("in", "not in"):
            return ["&" if op == "in" else "|", (new_left, "=", op == "not in"), leaf]
        return [(left, op, right)]

    def adapter_move(leaf, _or, _neg):
        # Adapt the selection value 'product' in `stock.move.product_type` to use
        # `is_storable` boolean field instead, before removal of `product_type`
        left, op, right = leaf
        if right == "product" or right == "consu" or isinstance(right, (tuple, list)) and len(right) == 1:
            path = left.split(".")
            path[-1] = "is_storable"
            new_left = ".".join(path)
            if "product" in right or right == "product":
                return [(new_left, "=", op in ("=", "in"))]
            elif "consu" in right or right == "consu":
                return [(new_left, "=", op not in ("=", "in"))]
        return [leaf]

    util.adapt_domains(cr, "product.template", "type", "type", adapter=adapter_product)
    util.change_field_selection_values(cr, "product.template", "type", {"product": "consu"})

    util.adapt_domains(cr, "stock.move", "product_type", "product_type", adapter=adapter_move)
    util.remove_field(cr, "stock.move", "product_type")
