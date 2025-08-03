from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("SELECT 1 FROM ir_module_module WHERE name = 'product' AND demo IS TRUE")
    if not cr.rowcount:
        return

    dup_xmlid = """
    INSERT INTO ir_model_data(module, name, model, res_id, noupdate)
         SELECT module, %s, model, res_id, true
           FROM ir_model_data
          WHERE module = 'product'
            AND name = %s
    """
    cr.execute(dup_xmlid, ["product_template_5", "product_product_5_product_template"])
    cr.execute(dup_xmlid, ["product_template_8", "product_product_8_product_template"])
    cr.execute(dup_xmlid, ["product_template_13", "product_product_13_product_template"])
    cr.execute(dup_xmlid, ["sofa_product_template", "consu_delivery_01_product_template"])

    # create product attribute line to keep product_product_8
    attribute_id = util.ref(cr, "product.fabric_attribute")
    template_id = util.ref(cr, "product.product_template_8")
    cr.execute(
        """
        INSERT INTO product_template_attribute_line (product_tmpl_id, attribute_id)
        VALUES (%(template_id)s, %(att_id)s)
        """,
        {"att_id": attribute_id, "template_id": template_id},
    )
    util.ensure_xmlid_match_record(
        cr,
        "product.product_8_fabric_attribute_line",
        "product.template.attribute.line",
        {"product_tmpl_id": template_id, "attribute_id": attribute_id},
    )

    # create product variants for consu_delivery_01
    template_id = util.ref(cr, "product.sofa_product_template")
    cr.execute(
        """
        WITH prod_att_value AS (
             INSERT INTO product_attribute_value (attribute_id, name, active)
             VALUES (%(att_id)s, '{"en_US": "Linen"}', TRUE),
                    (%(att_id)s, '{"en_US": "Velvet"}', TRUE),
                    (%(att_id)s, '{"en_US": "Leather"}', TRUE)
             RETURNING id
            ),
            prod_temp_att_line AS (
             INSERT INTO product_template_attribute_line (product_tmpl_id, attribute_id)
             VALUES (%(template_id)s, %(att_id)s)
             RETURNING id
            )
        INSERT INTO product_template_attribute_value (product_attribute_value_id, attribute_line_id,product_tmpl_id, attribute_id)
        SELECT prod_att_value.id,
               prod_temp_att_line.id,
               %(template_id)s,
               %(att_id)s
          FROM prod_att_value,
               prod_temp_att_line
      ORDER BY prod_att_value.id,
               prod_temp_att_line.id
     RETURNING id
        """,
        {"att_id": attribute_id, "template_id": template_id},
    )
    attribute_values = [id for (id,) in cr.fetchall()]
    util.ensure_xmlid_match_record(
        cr,
        "product.sofa_fabric_attribute_line",
        "product.template.attribute.line",
        {"product_tmpl_id": template_id, "attribute_id": attribute_id},
    )
    first_variant_id = util.ref(cr, "product.consu_delivery_01")
    cols = util.get_columns(
        cr,
        "product_product",
        ignore=(
            "id",
            "combination_indices",
        ),
    )
    for xmlid in ("product.consu_delivery_01_velvet", "product.consu_delivery_01_leather"):
        cr.execute(
            util.format_query(
                cr,
                """
                   INSERT INTO product_product({cols}, combination_indices)
                   SELECT {p_cols}, %s
                     FROM product_product p
                    WHERE p.id = %s
                RETURNING id
                """,
                cols=cols,
                p_cols=cols.using(alias="p"),
            ),
            [attribute_values[1 if "velvet" in xmlid else 2], first_variant_id],
        )
        (new_id,) = cr.fetchone()
        util.ensure_xmlid_match_record(cr, xmlid, "product.product", {"id": new_id})
