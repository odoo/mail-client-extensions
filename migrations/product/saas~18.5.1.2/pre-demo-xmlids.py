from odoo.upgrade import util

produc_demo_tools = util.import_script("product/saas~18.4.1.2/pre-demo-xmlids.py")


def migrate_demo(cr):
    # create variants for product_template_acoustic_bloc_screens
    template_screen_id = util.ref(cr, "product.product_template_acoustic_bloc_screens")
    first_variant_id = util.ref(cr, "product.product_product_25")
    color_attribute_id = util.ref(cr, "product.pa_color")
    att_black_id = util.ref(cr, "product.pav_color_black")
    cr.execute(
        """
        SELECT id FROM product_template_attribute_line WHERE product_tmpl_id = %s AND attribute_id = %s
        """,
        [template_screen_id, color_attribute_id],
    )
    (ptal_id,) = cr.fetchone()
    cr.execute(
        """
        SELECT id FROM product_template_attribute_value WHERE attribute_line_id = %s AND product_attribute_value_id = %s
        """,
        [ptal_id, att_black_id],
    )
    if cr.rowcount:
        (acoustic_ptav_black,) = cr.fetchone()
        cr.execute(
            """
            SELECT id
              FROM product_product
             WHERE product_tmpl_id = %s
               AND combination_indices = %s
            """,
            [template_screen_id, str(acoustic_ptav_black)],
        )
        (variant_id,) = cr.fetchone()
        util.ensure_xmlid_match_record(
            cr,
            "product.product_product_acoustic_bloc_screens_black",
            "product.product",
            {"id": variant_id},
        )
    else:
        acoustic_ptav_black = produc_demo_tools._create_tmpl_att_val(
            cr, "acoustic_ptav_black", template_screen_id, ptal_id, color_attribute_id, att_black_id
        )
        produc_demo_tools._create_variants(
            cr, "product_product_acoustic_bloc_screens_black", first_variant_id, [acoustic_ptav_black]
        )


def migrate(cr, version):
    cr.execute("SELECT 1 FROM ir_module_module WHERE name = 'product' AND demo IS TRUE")
    if cr.rowcount:
        migrate_demo(cr)
