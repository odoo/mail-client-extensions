def migrate(cr, version):
    cr.execute("SELECT count(id) FROM res_company")
    if cr.fetchone()[0] > 1:
        # Unarchive the 'Inter-company transit' in multi-company settings. As we're in post-migrate, the location should always exist.
        cr.execute(
            """
               UPDATE stock_location sl
                  SET active = true
                 FROM ir_model_data imd
                WHERE imd.name = 'stock_location_inter_company'
                  AND imd.module = 'stock'
                  AND imd.res_id = sl.id
            RETURNING sl.id
        """
        )
        inter_company_loc_id = cr.fetchone()[0]

        # For multi-company databases, we need to set the 'Inter-company transit' location as Customer/Vendor location
        # for the other companies' partners, from the POV of each company.
        # If an ir.property record already exist for that combination, we ignore it, as it may be user configuration.
        cr.execute(
            """
            INSERT INTO ir_property(name, company_id, type, fields_id, res_id, value_reference)
                 SELECT imf.name,
                        rca.id,
                        'many2one',
                        imf.id,
                        CONCAT('res.partner,', rcb.partner_id),
                        CONCAT('stock.location,', %s)
                   FROM res_company rca
             CROSS JOIN res_company rcb
                   JOIN ir_model_fields imf
                     ON imf.model = 'res.partner'
                    AND imf.name IN ('property_stock_customer', 'property_stock_supplier')
                  WHERE rca.id != rcb.id
            ON CONFLICT DO NOTHING
        """,
            [inter_company_loc_id],
        )

    # To maintain old pull rules behavior, we need to pre-set location_dest_from_rule on existing
    # pull rules that have different destinations than their picking types.
    cr.execute(
        """
        UPDATE stock_rule sr
           SET location_dest_from_rule = true
          FROM stock_picking_type spt
         WHERE spt.id = sr.picking_type_id
           AND sr.action IN ('pull', 'pull_push')
           AND sr.location_dest_id IS DISTINCT FROM spt.default_location_dest_id
    """
    )
