def migrate(cr, version):
    # Fill product_uom model with data from temporary table _upg_product_packaging_barcode
    cr.execute(
        """
        INSERT INTO product_uom (barcode, product_id, uom_id, company_id)
             SELECT ppb.barcode, ppb.product_id, ppb.uom_id, pt.company_id
               FROM _upg_product_packaging_barcode ppb
               JOIN product_product pp
                 ON pp.id = ppb.product_id
               JOIN product_template pt
                 ON pp.product_tmpl_id = pt.id
        """
    )
    cr.execute("DROP TABLE _upg_product_packaging_barcode")
