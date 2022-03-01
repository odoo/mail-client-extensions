def migrate(cr, version):
    cr.execute(
        """
        DELETE FROM product_pricelist_item i
              USING product_pricelist p
              WHERE p.id = i.pricelist_id
                AND i.active IS NOT TRUE
                AND p.active IS TRUE
        """
    )
