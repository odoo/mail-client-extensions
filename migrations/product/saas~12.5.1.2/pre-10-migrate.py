# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces

    cr.execute("SELECT active FROM ir_rule WHERE id = %s", [util.ref(cr, "product.product_comp_rule")])
    if not cr.rowcount or not cr.fetchone()[0]:
        # loutish technique to set a column to NULL
        # it's also O(1) instead of O(n) with an UPDATE
        util.remove_column(cr, "product_template", "company_id")
        util.create_column(cr, "product_template", "company_id", "int4")

    util.create_m2m(cr, "product_variant_combination", "product_template_attribute_value", "product_product")
    cr.execute(
        """
        INSERT INTO product_variant_combination(product_template_attribute_value_id, product_product_id)
             SELECT ptav.id, r.product_product_id
               FROM product_attribute_value_product_product_rel r
               JOIN product_product p
                 ON p.id = r.product_product_id
               JOIN product_template_attribute_value ptav
                 ON ptav.product_attribute_value_id = r.product_attribute_value_id
                AND ptav.product_tmpl_id = p.product_tmpl_id
    """
    )

    cr.execute("DROP TABLE product_attribute_value_product_product_rel CASCADE")
    # util.rename_field(cr, "product.product", "attribute_value_ids", "product_template_attribute_value_ids")
    util.remove_field(cr, "product.product", "attribute_value_ids")

    util.create_column(cr, "product_product", "combination_indices", "varchar")
    cr.execute(
        """
        WITH indices AS (
            SELECT product_product_id,
                   string_agg(product_template_attribute_value_id::TEXT, ','::TEXT ORDER BY product_template_attribute_value_id) indice
              FROM product_variant_combination
          GROUP BY product_product_id
        )
        UPDATE product_product p
           SET combination_indices = i.indice
          FROM indices i
         WHERE i.product_product_id = p.id
    """  # noqa: B950
    )
    cr.execute("UPDATE product_product SET combination_indices = '' WHERE combination_indices IS NULL")

    util.remove_field(cr, "product.product", "pricelist_item_ids")
    # NOTE: image fields are handled in `pre-image.py`

    util.create_column(cr, "product_packaging", "company_id", "int4")

    util.create_m2m(cr, "product_attribute_product_template_rel", "product_attribute", "product_template")
    cr.execute(
        """
        INSERT INTO product_attribute_product_template_rel(product_attribute_id, product_template_id)
             SELECT attribute_id, product_tmpl_id
               FROM product_template_attribute_line
         ON CONFLICT DO NOTHING
    """
    )

    util.create_column(cr, "product_template_attribute_line", "active", "boolean")
    cr.execute("UPDATE product_template_attribute_line SET active=true")

    util.create_column(cr, "product_template_attribute_value", "ptav_active", "boolean", default=True)
    util.create_column(cr, "product_template_attribute_value", "attribute_id", "int4")
    util.create_column(cr, "product_template_attribute_value", "attribute_line_id", "int4")
    util.remove_field(cr, "product.template.attribute.value", "sequence")

    query = """
            UPDATE product_template_attribute_value tv
               SET attribute_id = pv.attribute_id
              FROM product_attribute_value pv
             WHERE pv.id = tv.product_attribute_value_id
    """
    util.parallel_execute(
        cr, util.explode_query_range(cr, query, table="product_template_attribute_value", prefix="tv.")
    )

    query = """
            UPDATE product_template_attribute_value v
               SET attribute_line_id = l.id
              FROM product_template_attribute_line l
             WHERE l.product_tmpl_id = v.product_tmpl_id
               AND l.attribute_id = v.attribute_id
    """
    util.parallel_execute(
        cr, util.explode_query_range(cr, query, table="product_template_attribute_value", prefix="v.")
    )

    util.create_column(cr, "product_pricelist_item", "active", "boolean")
    cr.execute(
        """
        UPDATE product_pricelist_item i
           SET active = l.active
          FROM product_pricelist l
         WHERE l.id = i.pricelist_id
    """
    )
    cr.execute("UPDATE product_pricelist_item SET compute_price='fixed' WHERE compute_price IS NULL")

    util.remove_field(cr, "product.template", "valid_product_attribute_value_ids")
    util.remove_field(cr, "product.template", "valid_product_attribute_ids")
    util.remove_field(cr, "product.template", "valid_product_template_attribute_line_wnva_ids")
    util.remove_field(cr, "product.template", "valid_product_attribute_value_wnva_ids")
    util.remove_field(cr, "product.template", "valid_product_attribute_wnva_ids")
    util.remove_field(cr, "product.template", "valid_archived_variant_ids")
    util.remove_field(cr, "product.template", "valid_existing_variant_ids")
    util.remove_field(cr, "product.template", "item_ids")

    util.move_field_to_module(
        cr, "product.template", "has_configurable_attributes", "sale_product_configurator", "product"
    )
    util.create_column(cr, "product_template", "has_configurable_attributes", "boolean")
    cr.execute(
        """
      WITH lines AS (
          SELECT l.id, l.product_tmpl_id, a.create_variant, count(r.product_attribute_value_id) as value_count
            FROM product_attribute_value_product_template_attribute_line_rel r
            JOIN product_template_attribute_line l ON l.id = r.product_template_attribute_line_id
            JOIN product_attribute a ON a.id = l.attribute_id
        GROUP BY l.id, l.product_tmpl_id, a.create_variant
          HAVING a.create_variant = 'dynamic' OR count(r.product_attribute_value_id) >= 2
      )
      UPDATE product_template t
         SET has_configurable_attributes = id IN (SELECT product_tmpl_id FROM lines)
       WHERE has_configurable_attributes IS NULL
    """
    )

    util.remove_field(cr, "res.config.settings", "company_share_product")
    util.remove_field(cr, "res.config.settings", "group_pricelist_item")
    util.move_field_to_module(cr, "res.config.settings", "group_discount_per_so_line", "sale", "product")
    util.create_column(cr, "res_config_settings", "group_discount_per_so_line", "boolean")
    util.create_column(cr, "res_config_settings", "module_sale_product_matrix", "boolean")
    util.create_column(cr, "res_config_settings", "product_pricelist_setting", "varchar")

    cr.execute(
        """
        INSERT INTO res_groups_users_rel(uid, gid)
             SELECT uid, %(adv)s
               FROM res_groups_users_rel
              WHERE gid = %(item)s
             EXCEPT
             SELECT uid, gid
               FROM res_groups_users_rel
              WHERE gid = %(adv)s
    """,
        {"adv": util.ref(cr, "product.group_sale_pricelist"), "item": util.ref(cr, "product.group_pricelist_item")},
    )

    # data
    util.remove_record(cr, "product.group_pricelist_item")
    util.force_noupdate(cr, "product.group_sale_pricelist", noupdate=False)
    util.rename_xmlid(cr, *eb("{sale,product}.group_discount_per_so_line"))
    util.remove_view(cr, "product.variants_tree_view")
    util.remove_record(cr, "product.variants_action")
