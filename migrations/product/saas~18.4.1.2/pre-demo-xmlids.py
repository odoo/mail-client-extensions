from odoo.upgrade import util
from odoo.upgrade.util.misc import _cached


@_cached
def _get_product_columns(cr):
    return util.get_columns(
        cr,
        "product_product",
        ignore=(
            "id",
            "combination_indices",
        ),
    )


def _create_att_line(cr, xmlid, template_id, attribute_id):
    cr.execute(
        """
        INSERT INTO product_template_attribute_line (product_tmpl_id, attribute_id)
        VALUES (%s, %s)
        RETURNING id
        """,
        (template_id, attribute_id),
    )
    (new_id,) = cr.fetchone()
    util.ensure_xmlid_match_record(
        cr,
        f"product.{xmlid}",
        "product.template.attribute.line",
        {"id": new_id},
    )
    return new_id


def _create_tmpl_att_val(cr, xmlid, template_id, att_line_id, attribute_id, pav):
    cr.execute(
        """
        INSERT INTO product_template_attribute_value (product_attribute_value_id, attribute_line_id,product_tmpl_id, attribute_id)
        Values (%s, %s, %s, %s)
    RETURNING id
        """,
        [pav, att_line_id, template_id, attribute_id],
    )
    (new_id,) = cr.fetchone()
    util.ensure_xmlid_match_record(
        cr,
        f"product.{xmlid}",
        "product.template.attribute.value",
        {"id": new_id},
    )
    return new_id


def _create_variants(cr, xmlid, first_variant_id, attributes):
    indices = ",".join([str(att) for att in attributes])
    product_cols = _get_product_columns(cr)
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
            cols=product_cols,
            p_cols=product_cols.using(alias="p"),
        ),
        [indices, first_variant_id],
    )
    (new_id,) = cr.fetchone()
    util.ensure_xmlid_match_record(cr, f"product.{xmlid}", "product.product", {"id": new_id})


def migrate_demo(cr):
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
    cr.execute(dup_xmlid, ["pa_fabric", "fabric_attribute"])
    cr.execute(dup_xmlid, ["pa_legs", "product_attribute_1"])
    cr.execute(dup_xmlid, ["pav_legs_steel", "product_attribute_value_1"])
    cr.execute(dup_xmlid, ["pav_legs_aluminium", "product_attribute_value_2"])
    cr.execute(dup_xmlid, ["pa_color", "product_attribute_2"])
    cr.execute(dup_xmlid, ["pav_color_white", "product_attribute_value_3"])
    cr.execute(dup_xmlid, ["pav_color_black", "product_attribute_value_4"])

    # create product attributes
    fabric_attribute_id = util.ref(cr, "product.pa_fabric")
    leg_attribute_id = util.ref(cr, "product.pa_legs")
    attributes = [
        {
            "type": "fabric",
            "values": ["Linen", "Velvet", "Leather", "Wood", "Glass", "Metal"],
            "attribute_id": fabric_attribute_id,
        },
        {
            "type": "legs",
            "values": ["Wood", "Custom"],
            "attribute_id": leg_attribute_id,
        },
    ]
    for attribute in attributes:
        for val in attribute["values"]:
            cr.execute(
                """
                INSERT INTO product_attribute_value (attribute_id, name, active)
                VALUES (%s, jsonb_build_object('en_US', %s), TRUE)
            RETURNING id
                """,
                [attribute["attribute_id"], val],
            )
            (v_id,) = cr.fetchone()
            util.ensure_xmlid_match_record(
                cr,
                f"product.pav_{attribute['type']}_{val.lower()}",
                "product.attribute.value",
                {"id": v_id},
            )

    # create product variants for product_product_8
    template_8_id = util.ref(cr, "product.product_template_8")
    first_variant_id = util.ref(cr, "product.product_product_8")
    product_8_fabric_line = _create_att_line(cr, "product_8_fabric_attribute_line", template_8_id, fabric_attribute_id)
    product_8_glass_pav = _create_tmpl_att_val(
        cr,
        "pav_large_desk_glass",
        template_8_id,
        product_8_fabric_line,
        fabric_attribute_id,
        util.ref(cr, "product.pav_fabric_glass"),
    )
    product_8_metal_pav = _create_tmpl_att_val(
        cr,
        "pav_large_desk_metal",
        template_8_id,
        product_8_fabric_line,
        fabric_attribute_id,
        util.ref(cr, "product.pav_fabric_metal"),
    )
    _create_variants(cr, "product_product_8_glass", first_variant_id, [product_8_glass_pav])
    _create_variants(cr, "product_product_8_metal", first_variant_id, [product_8_metal_pav])

    # create product variants for consu_delivery_01
    template_sofa_id = util.ref(cr, "product.sofa_product_template")
    first_variant_id = util.ref(cr, "product.consu_delivery_01")
    sofa_fabric_attribute_line = _create_att_line(
        cr, "sofa_fabric_attribute_line", template_sofa_id, fabric_attribute_id
    )
    sofa_velvet_pav = _create_tmpl_att_val(
        cr,
        "pav_sofa_velvet",
        template_sofa_id,
        sofa_fabric_attribute_line,
        fabric_attribute_id,
        util.ref(cr, "product.pav_fabric_velvet"),
    )
    sofa_leather_pav = _create_tmpl_att_val(
        cr,
        "pav_sofa_leather",
        template_sofa_id,
        sofa_fabric_attribute_line,
        fabric_attribute_id,
        util.ref(cr, "product.pav_fabric_leather"),
    )
    _create_variants(cr, "consu_delivery_01_velvet", first_variant_id, [sofa_velvet_pav])
    _create_variants(cr, "consu_delivery_01_leather", first_variant_id, [sofa_leather_pav])

    # create product variants for product_product_4
    template_4_id = util.ref(cr, "product.product_product_4_product_template")
    first_variant_id = util.ref(cr, "product.product_product_4")
    attribute_line_id = util.ref(cr, "product.product_4_attribute_1_product_template_attribute_line")
    attribute_value_id = util.ref(cr, "product.pav_legs_custom")
    p4_white = util.ref(cr, "product.product_4_attribute_2_value_1")
    p4_black = util.ref(cr, "product.product_4_attribute_2_value_2")
    p4_leg_custom = _create_tmpl_att_val(
        cr, "product_4_attribute_1_value_3", template_4_id, attribute_line_id, leg_attribute_id, attribute_value_id
    )
    _create_variants(cr, "product_product_4e", first_variant_id, [p4_white, p4_leg_custom])
    _create_variants(cr, "product_product_4f", first_variant_id, [p4_black, p4_leg_custom])


def migrate(cr, version):
    cr.execute("SELECT 1 FROM ir_module_module WHERE name = 'product' AND demo IS TRUE")
    if cr.rowcount:
        migrate_demo(cr)
