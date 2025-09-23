from odoo.upgrade import util

produc_demo_tools = util.import_script("product/saas~18.4.1.2/pre-demo-xmlids.py")


def migrate_demo(cr):
    # create variants for product_template_acoustic_bloc_screens
    template_screen_id = util.ref(cr, "product.product_template_acoustic_bloc_screens")
    first_variant_id = util.ref(cr, "product.product_product_25")
    color_attribute_id = util.ref(cr, "product.pa_color")
    cr.execute(
        """
        SELECT id FROM product_template_attribute_line WHERE product_tmpl_id = %s AND attribute_id = %s
        """,
        [template_screen_id, color_attribute_id],
    )
    (ptal_id,) = cr.fetchone()
    for color in ("white", "black"):
        att_id = util.ref(cr, f"product.pav_color_{color}")
        cr.execute(
            """
            SELECT id FROM product_template_attribute_value
             WHERE attribute_line_id = %s
               AND product_attribute_value_id = %s
            """,
            [ptal_id, att_id],
        )
        if cr.rowcount:
            (acoustic_ptav,) = cr.fetchone()
            cr.execute(
                """
                SELECT id
                  FROM product_product
                 WHERE product_tmpl_id = %s
                   AND combination_indices = %s
                """,
                [template_screen_id, str(acoustic_ptav)],
            )
            (variant_id,) = cr.fetchone()
            util.ensure_xmlid_match_record(
                cr,
                f"product.product_product_acoustic_bloc_screens_{color}",
                "product.product",
                {"id": variant_id},
            )
        else:
            acoustic_ptav = produc_demo_tools._create_tmpl_att_val(
                cr, f"acoustic_ptav_{color}", template_screen_id, ptal_id, color_attribute_id, att_id
            )
            produc_demo_tools._create_variants(
                cr, f"product_product_acoustic_bloc_screens_{color}", first_variant_id, [acoustic_ptav]
            )


def migrate(cr, version):
    cr.execute("SELECT 1 FROM ir_module_module WHERE name = 'product' AND demo IS TRUE")
    if cr.rowcount:
        migrate_demo(cr)
