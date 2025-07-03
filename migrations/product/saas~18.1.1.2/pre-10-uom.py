from odoo.upgrade import util


def migrate(cr, version):
    util.create_m2m(cr, "product_template_uom_uom_rel", "product_template", "uom_uom")

    # Create a temporary column to store the new uom_id
    util.create_column(cr, "product_packaging", "_upg_temp_uom_id", "int4")
    # Squash all the packagings that share the same quantity and base unit into one `uom_uom` record
    # Then, update the `product_packaging` temporary column with the new `uom_uom` id to be used in later updates
    cr.execute(
        """
        WITH packaging_data AS (
            SELECT pp1.qty, pt.uom_id, pp1.name, COUNT(*) AS name_count
              FROM product_packaging pp1
              JOIN product_product pp2
                ON pp1.product_id = pp2.id
              JOIN product_template pt
                ON pp2.product_tmpl_id = pt.id
          GROUP BY pp1.qty, pt.uom_id, pp1.name
        ),
        ranked_packaging AS (
            SELECT pd.qty,
                   pd.uom_id,
                   pd.name,
                   pd.name_count,
                   RANK() OVER (
                        PARTITION BY pd.qty, pd.uom_id
                        ORDER BY pd.name_count DESC, pd.name ASC
                   ) AS rank,
                   COUNT(*) OVER (
                       PARTITION BY pd.qty, pd.uom_id, pd.name_count
                   ) AS tie_count -- Checks if there are names that are equally popular
              FROM packaging_data pd
        ),
        final_packaging AS (
            SELECT DISTINCT rp.qty,
                            rp.uom_id,
                            CASE
                                WHEN rp.rank = 1 AND rp.tie_count = 1 THEN rp.name
                                ELSE 'Pack ' || rp.qty
                            END AS final_name
                      FROM ranked_packaging rp
                     WHERE rp.rank = 1
        ),
        inserted_uom AS (
            INSERT INTO uom_uom (name, relative_factor, factor, relative_uom_id, active)
            SELECT jsonb_build_object('en_US', final_name) AS name,
                   qty AS relative_factor,
                   qty AS factor,
                   uom_id AS relative_uom_id,
                   TRUE AS active
              FROM final_packaging
                ON CONFLICT DO NOTHING
         RETURNING id, relative_factor, relative_uom_id
        ),
        packaging_update_data AS (
            SELECT pp1.id AS packaging_id,
                   MIN(iu.id) as uom_id
              FROM product_packaging pp1
              JOIN product_product pp2
                ON pp1.product_id = pp2.id
              JOIN product_template pt
                ON pp2.product_tmpl_id = pt.id
              JOIN inserted_uom iu
                ON pp1.qty = iu.relative_factor
               AND pt.uom_id = iu.relative_uom_id
          GROUP BY pp1.id
        )
        UPDATE product_packaging
           SET _upg_temp_uom_id = pud.uom_id
          FROM packaging_update_data AS pud
         WHERE product_packaging.id = pud.packaging_id
        """
    )
    # Set the new uom_id as a packaging unit for the product(s) that had packaging(s) with the same quantity and base unit, only for packagings that were used for sales
    if util.column_exists(cr, "product_packaging", "sales"):
        cr.execute("""
            INSERT INTO product_template_uom_uom_rel (product_template_id, uom_uom_id)
                SELECT product.product_tmpl_id AS product_template_id, packaging._upg_temp_uom_id AS uom_id
                FROM product_packaging packaging
                JOIN product_product product
                    ON packaging.product_id = product.id
                WHERE packaging.sales = TRUE
            GROUP BY product.product_tmpl_id, packaging._upg_temp_uom_id
        """)
    # Create a temporary table to store barcodes
    cr.execute("""
        CREATE TABLE _upg_product_packaging_barcode (
            product_id INT4 NOT NULL REFERENCES product_product(id) ON DELETE CASCADE,
                uom_id INT4 NOT NULL REFERENCES uom_uom(id) ON DELETE CASCADE,
               barcode VARCHAR(64) NOT NULL,
            PRIMARY KEY (product_id, uom_id, barcode)
        );
        INSERT INTO _upg_product_packaging_barcode (product_id, uom_id, barcode)
             SELECT pp.product_id, pp._upg_temp_uom_id, pp.barcode
               FROM product_packaging pp
              WHERE pp.barcode IS NOT NULL
           GROUP BY pp.product_id, pp._upg_temp_uom_id, pp.barcode
    """)
    util.remove_column(cr, "product_packaging", "_upg_temp_uom_id")

    util.remove_record(cr, "product.product_packaging_comp_rule")
    util.remove_record(cr, "product.report_product_packaging")
    util.remove_group(cr, "product.group_stock_packaging")
    util.merge_model(cr, "product.packaging", "uom.uom")
    util.remove_field(cr, "res.config.settings", "group_stock_packaging")
    util.remove_field(cr, "product.template", "packaging_ids")
    util.remove_field(cr, "product.template", "uom_po_id")
    util.remove_field(cr, "product.template", "uom_category_id")
    util.remove_field(cr, "product.product", "packaging_ids")

    util.remove_view(cr, "product.product_packaging_form_view")
    util.remove_view(cr, "product.product_packaging_form_view2")
    util.remove_view(cr, "product.product_packaging_tree_view")
    util.remove_view(cr, "product.product_packaging_tree_view2")
    util.remove_view(cr, "product.product_packaging_search_view")
